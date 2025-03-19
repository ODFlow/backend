import sqlite3
import requests
import json
import pandas as pd

from datetime import datetime
from itertools import product
from typing import Dict, Any


class TrafficAccidentFetcher:

    def __init__(self, api_url: str, query_parameters_file: str, db_name: str):
        self.api_url = api_url
        self.query_parameters_file = query_parameters_file
        self.db_name = db_name

        with open(query_parameters_file, 'r') as file:
            query_data = json.load(file)
            self.query_parameters = query_data['queryObj']

    def fetch_data(self) -> Dict[str, Any]:
        response = requests.post(url=self.api_url, json=self.query_parameters)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def create_table(cursor: sqlite3.Cursor):
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS traffic_accidents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        area TEXT NOT NULL,
                        year TEXT NOT NULL,
                        description TEXT NOT NULL,
                        value INTEGER NOT NULL,
                        last_updated TEXT NOT NULL,
                        UNIQUE (area)
                    )
                ''')

    @staticmethod
    def parse_data(data: Dict[str, Any]) -> pd.DataFrame:
        areas = list(data['dimension']['Alue']['category']['label'].values())
        years = list(data['dimension']['Vuosi']['category']['label'].values())
        accident_types = list(
            data['dimension']['Tiedot']['category']['label'].values())

        combinations = product(areas, years, accident_types)
        values = data['value']

        records = []
        for idx, (area, year, accident_type) in enumerate(combinations):
            value = values[idx]
            records.append(
                (idx, area, year, accident_type, value, LAST_UPDATED_TIME))

        return pd.DataFrame(records,
                            columns=[
                                'id', 'area', 'year', 'description', 'value',
                                'last_updated'
                            ])

    def save_data(self, df: pd.DataFrame):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        self.create_table(cursor)
        df.to_sql('traffic_accidents', conn, if_exists='replace', index=False)

        conn.commit()
        conn.close()

    def fetch_parse_save(self):
        try:
            data = self.fetch_data()
            df = self.parse_data(data=data)
            self.save_data(df=df)
            print("Success")

        except requests.exceptions.RequestException as e:
            print(f"{e}")

        except Exception as e:
            print(f"{e}")


if __name__ == '__main__':
    LAST_UPDATED_TIME = datetime.now()
    URL = 'https://pxdata.stat.fi:443/PxWeb/api/v1/en/StatFin/ton/statfin_ton_pxt_12qh.px'
    JSON_PARAMS = '../../config/traffic_accidents_general.json'
    DB = '../../db/combined_db.sqlite3'
    f = TrafficAccidentFetcher(api_url=URL,
                               query_parameters_file=JSON_PARAMS,
                               db_name=DB)
    f.fetch_parse_save()
