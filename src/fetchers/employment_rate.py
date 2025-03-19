import json
import sqlite3
from datetime import datetime
from itertools import product
from typing import Dict, Any

import pandas as pd
import requests


class EmploymentRateFetcher:

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
                    CREATE TABLE IF NOT EXISTS employment_rate (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        area TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        description TEXT NOT NULL,
                        value REAL NOT NULL,
                        last_updated TEXT NOT NULL,
                        UNIQUE (area, timeframe)
                    )
                ''')

    @staticmethod
    def parse_data(data: Dict[str, Any]) -> pd.DataFrame:
        areas = list(data['dimension']['Alue']['category']['label'].values())
        timeframe = list(
            data['dimension']['Kuukausi']['category']['label'].values())
        description = list(
            data['dimension']['Tiedot']['category']['label'].values())

        combinations = product(areas, timeframe, description)
        values = data['value']

        records = []
        for idx, (area, timeframe, description) in enumerate(combinations):
            value = values[idx]
            records.append(
                (idx, area, timeframe, description, value, LAST_UPDATED_TIME))

        return pd.DataFrame(records,
                            columns=[
                                'id', 'area', 'timeframe', 'description',
                                'value', 'last_updated'
                            ])

    def save_data(self, df: pd.DataFrame):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        self.create_table(cursor)
        df.to_sql('employment_rate', conn, if_exists='replace', index=False)

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
    URL = 'https://pxdata.stat.fi:443/PxWeb/api/v1/en/StatFin/tyonv/statfin_tyonv_pxt_12r5.px'
    JSON_PARAMS = '../../config/crime_rate.json'
    DB = '../../db/combined_db.sqlite3'
    f = EmploymentRateFetcher(api_url=URL,
                              query_parameters_file=JSON_PARAMS,
                              db_name=DB)
    f.fetch_parse_save()
