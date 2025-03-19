import json
import os
import sqlite3
from datetime import datetime
from itertools import product
from typing import Dict, Any

import pandas as pd
import requests


class IncomeFetcher:

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
                    CREATE TABLE IF NOT EXISTS income (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        area TEXT NOT NULL,
                        description TEXT NOT NULL,
                        value REAL NOT NULL,
                        last_updated TEXT NOT NULL,
                        UNIQUE (area)
                    )
                ''')

    @staticmethod
    def parse_data(data: Dict[str, Any]) -> pd.DataFrame:
        area = list(data['dimension']['Alue']['category']['label'].values())
        raw_description = list(
            data['dimension']['Tiedot']['category']['label'].values())

        clean_description = []
        for i in raw_description:
            if ' ' in i:
                first_space_ind = i.find(' ')
                if not i[:first_space_ind].isalpha():
                    clean_description.append(i[first_space_ind + 1:])
                else:
                    clean_description.append(i)
            else:
                clean_description.append(i)

        combinations = product(clean_description, area)
        values = data['value']

        records = []

        for idx, (description, area) in enumerate(combinations):
            val = values[idx]
            records.append((idx, area, description, val, LAST_UPDATED_TIME))

        return pd.DataFrame(
            records,
            columns=['id', 'area', 'description', 'value', 'last_updated'])

    def save_data(self, df: pd.DataFrame):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        self.create_table(cursor)
        df.to_sql('income', conn, if_exists='replace', index=False)

        conn.commit()
        conn.close()

    def fetch_parse_save(self):
        try:
            data = self.fetch_data()
            df = self.parse_data(data)
            self.save_data(df)
            print("Success")

        except requests.exceptions.RequestException as e:
            print(f"{e}")

        except Exception as e:
            print(f"{e}")


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    LAST_UPDATED_TIME = datetime.now()
    URL = 'https://pxdata.stat.fi:443/PxWeb/api/v1/en/StatFin/tjt/statfin_tjt_pxt_118w.px'
    JSON_PARAMS = os.path.join(BASE_DIR, "config", "income.json")
    DB = os.path.join(BASE_DIR, "db", "combined_db.sqlite3")
    f = IncomeFetcher(api_url=URL,
                      query_parameters_file=JSON_PARAMS,
                      db_name=DB)
    f.fetch_parse_save()
