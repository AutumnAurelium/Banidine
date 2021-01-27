import sqlite3
from datetime import datetime

from substrate import Universe

if __name__ == '__main__':
    eve = Universe()

    type_id = 34
    type_name = eve.get_item_name(type_id)

    data = eve.get_market_orders(eve.get_region_id("The Forge"), type_id)

    db = sqlite3.connect("sleeper/scraped_data.sqlite")
    conn = db.cursor()

    tableName = "marketOrders"

    conn.execute(f"""
CREATE TABLE IF NOT EXISTS {tableName}(
    OrderID int,
    Duration time,
    BuyOrder boolean,
    Issued datetime,
    LocationID int,
    MinVolume int,
    Price float,
    Range varchar(16),
    SystemID int,
    TypeID int,
    TypeName int,
    VolumeRemaining int,
    VolumeTotal int,
    TimeCached datetime
)
    """)
    for i in range(data.shape[0]):
        entry = data.iloc[i, :]
        conn.execute(f"""
    INSERT INTO {tableName} VALUES (
    '{entry['order id']}',
    '{entry['duration']}',
    '{entry['is buy order']}',
    '{entry['issued']}',
    '{entry['location id']}',
    '{entry['minimum volume']}',
    '{entry['price']}',
    '{entry['range']}',
    '{entry['system id']}',
    '{entry['type id']}',
    '{type_name}',
    '{entry['volume remaining']}',
    '{entry['volume total']}',
    '{datetime.now().replace(second=0, microsecond=0, minute=0)}'
    )
        """)

    db.commit()
    db.close()
