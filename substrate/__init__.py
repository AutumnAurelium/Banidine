import sqlite3
from typing import List, Dict

from swagger_client.api.market_api import MarketApi
import pandas as pd

TypeID = int


class Universe:
    def __init__(self):
        self.db = sqlite3.connect("data/eve.sqlite", check_same_thread=False)
        self.conn = self.db.cursor()
        self.market = MarketApi()

    def get_valid_items(self) -> List[TypeID]:
        return self.conn.execute("SELECT typeID FROM invTypes WHERE typeID > 30").fetchall()

    def get_valid_item_names(self) -> List[TypeID]:
        return self.conn.execute("SELECT typeName FROM invTypes WHERE typeID > 30 AND typeID < ").fetchall()

    def get_item_id(self, type_name: str) -> TypeID:
        """
        Gets an item by its English name.
        :param type_name: The name of the region. Case sensitive.
        :return: The region ID for use in the API.
        """
        try:
            return self.conn.execute("SELECT typeID FROM invTypes WHERE typeName IS ?", [type_name]).fetchone()[0]
        except sqlite3.Error:
            return -1
        except TypeError:
            return -1

    def get_region_id(self, region_name: str) -> int:
        """
        Gets an item by its English name.
        :param region_name: The name of the region. Case sensitive.
        :return: The region ID for use in the API.
        """
        try:
            return self.conn.execute("SELECT regionID FROM mapRegions WHERE regionName IS ?", [region_name]).fetchone()[
                0]
        except sqlite3.Error:
            return -1
        except TypeError:
            return -1

    def get_item_name(self, type_id: TypeID) -> str:
        """
        Gets the English name of an item by type_id.
        :param type_id: The type ID of the item.
        :return: The name of the item, or UNK[#type_id] if one cannot be found.
        """
        try:
            return self.conn.execute("SELECT typeName FROM invTypes WHERE typeID IS ?", [type_id]).fetchone()[0]
        except sqlite3.Error:
            return f"UNK[#{type_id}]"
        except TypeError:
            return f"UNK[#{type_id}]"

    def get_region_name(self, region_id: TypeID) -> str:
        """
        Gets the English name of an item by type_id.
        :param region_id: The region's ID.
        :return: The name of the item, or UNK_REGION[#region_id] if one cannot be found.
        """
        try:
            return self.conn.execute("SELECT regionName FROM mapRegions WHERE regionID IS ?", [region_id]).fetchone()[0]
        except sqlite3.Error:
            return f"UNK_REGION[#{region_id}]"
        except TypeError:
            return f"UNK_REGION[#{region_id}]"

    def get_price(self, type_id: TypeID) -> float:
        """
        Gets the
        :param type_id: The type ID of the item.
        :return: The average market price of an item. May not be reflective of actual prices at trade hubs.
        """
        prices = self.market.get_markets_prices()

        for entry in prices:
            if entry.type_id == type_id:
                return entry.average_price

        raise KeyError(f"Could not fetch market price for {self.get_item_name(type_id)}")

    def get_item_names_with_market_orders(self) -> List[str]:
        prices = self.market.get_markets_prices()
        items = []
        for entry in prices:
            items.append(self.get_item_name(entry.type_id))
        return items

    def get_market_history(self, region_id: int, type_id: TypeID) -> pd.DataFrame:
        response = self.market.get_markets_region_id_history(region_id, type_id)
        records = [x.__dict__ for x in response]
        df = pd.DataFrame.from_records(records)
        df.columns = ["average", "date", "highest", "lowest", "order count", "volume", "discriminator"]
        df = df.drop(["discriminator"], axis=1)
        return df

    def get_market_orders(self, region_id: int, type_id: TypeID, start_page=1, pages=-1, progress=False) -> pd.DataFrame:
        response = []
        all = []
        page = start_page
        while (len(response) == 1000 or page == 1) and (page <= pages or pages == -1):
            response = self.market.get_markets_region_id_orders("all", region_id, page=page, type_id=type_id)
            for x in response:
                all.append(x)
            if progress:
                print(f"Downloaded market page {page}.")
            page += 1

        records = [x.__dict__ for x in all]
        df = pd.DataFrame.from_records(records)
        df.columns = ["duration", "is buy order", "issued", "location id", "minimum volume", "order id", "price", "range", "system id", "type id", "volume remaining", "volume total", "discriminator"]
        df = df.drop(["discriminator"], axis=1)
        return df
