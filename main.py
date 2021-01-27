from dash import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State
from plotly.subplots import make_subplots

from substrate import Universe

eve = Universe()

app = dash.Dash(__name__)

df = eve.get_market_history(eve.get_region_id("The Forge"), eve.get_item_id("Heron"))

fig = go.Figure()

app.layout = html.Div(children=[
    dcc.Graph(
        id='price-graph',
        figure=fig
    ),
    html.Div(["Item: ",
      dcc.Dropdown(id='item-name', value='Heron', options=[
          {"label": x, "value": x} for x in eve.get_item_names_with_market_orders()
      ])]),
])


@app.callback(
    Output(component_id='price-graph', component_property='figure'),
    Input(component_id='item-name', component_property='value'),
    State(component_id='price-graph', component_property="figure")
)
def update_output_div(input_value, prev_figure):
    item_id = eve.get_item_id(input_value.title())
    if item_id != -1:
        df = eve.get_market_history(eve.get_region_id("The Forge"), item_id)
        fig = make_subplots(
            rows=1, cols=1,
            specs=[[{"secondary_y": True}]],
            horizontal_spacing=0.1)

        fig.add_trace(go.Scatter(name="average price", x=df["date"], y=df["average"]), row=1, col=1)
        fig.add_trace(go.Bar(name="volume", x=df["date"], y=df["volume"], opacity=0.5), row=1, col=1, secondary_y=True)

        fig.update_layout()

        return fig
    return prev_figure


app.run_server("127.0.0.1", 8080)
