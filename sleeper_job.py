import sqlite3
from datetime import datetime

from substrate import Universe

if __name__ == '__main__':
    eve = Universe()

    with open("sleeper/watchlist.txt") as f:
        lines = f.readlines()

    for type_name in lines:
        type_name = type_name.strip()
        if type_name.startswith("#"):
            continue
        if type_name == "":
            continue

        type_id = eve.get_item_id(type_name)

        if type_id == -1:
            print(f"Warning: Invalid item name: {type_name}")
            continue

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
