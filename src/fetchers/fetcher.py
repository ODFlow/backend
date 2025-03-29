import json
import os
import sqlite3
from datetime import datetime
from itertools import product
from typing import Dict, Any

import logging
import pandas as pd
import requests

logger = logging.getLogger("fetchers")


class Fetcher:

    def __init__(self, api_url: str, query_parameters_file: str, db_name: str,
                 table_name: str, columns: list[str], area_path: str,
                 description_path: str, timeframe_path: str, age_path: str,
                 combinations_order: list[str]):

        self.api_url = api_url
        self.query_parameters_file = query_parameters_file
        self.db_name = db_name
        self.table_name = table_name
        self.columns = columns
        self.area_path = area_path
        self.description_path = description_path
        self.timeframe_path = timeframe_path
        self.age_path = age_path
        self.combinations_order = combinations_order

        with open(self.query_parameters_file, 'r') as file:
            query_data = json.load(file)
            self.query_parameters = query_data['queryObj']



    def fetch_data(self) -> Dict[str, Any]:
        """

        Returns: Dictionary with the json formatted data

        """
        logger.info("[-] Fetching data for %s", self.table_name)
        response = requests.post(url=self.api_url,
                                 json=self.query_parameters,
                                 timeout=5)
        response.raise_for_status()
        return response.json()



    def parse_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """

        Args:
            data (Dict[str, Any]): Json formatted data

        Returns:
            pd.DataFrame: Dataframe containing the parsed data

        """

        logger.info(f"[-] Parsing data for {self.table_name}")
        dimensions = {
            'area':
                list(data['dimension'][self.area_path]['category']['label'].
                     values()) if self.area_path in data['dimension'] else [],
            'description':
                list(data['dimension'][self.description_path]['category']
                     ['label'].values())
                if self.description_path in data['dimension'] else [],
            'timeframe':
                list(data['dimension'][self.timeframe_path]['category']
                     ['label'].values()) if self.timeframe_path != '' and
                self.timeframe_path in data['dimension'] else [],
            'age':
                list(data['dimension'][self.age_path]['category']
                     ['label'].values()) if self.age_path != '' and
                self.age_path in data['dimension'] else []
        }

        param_lists = [dimensions[param] for param in self.combinations_order]
        values = data['value']

        records = []
        for idx, combo in enumerate(product(*param_lists)):

            if idx >= len(values):
                break

            param_values = dict(zip(self.combinations_order, combo))
            record = [idx]

            for c in self.columns[1:-2]:

                record.append(param_values.get(c))

            record.append(values[idx])
            record.append(LAST_UPDATED_TIME)
            records.append(tuple(record))

        logger.info("[✓] Successfully parsed %s records in %s", len(records),
                    self.db_name)
        return pd.DataFrame(records, columns=self.columns)



    def save_data(self, df: pd.DataFrame):
        """

        Args:
            df (pd.DataFrame): Dataframe to be saved

        Returns:
            None: This function does not return a value

        """
        try:
            conn = sqlite3.connect(self.db_name)
            df.to_sql(self.table_name, conn, if_exists='replace', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error("Data db saving error for %s", self.table_name)
            raise

        except Exception as e:
            logger.error("Error saving data for %s", self.table_name)
            raise



    def fetch_parse_save(self) -> bool:
        """

        Returns:
            bool: True if success, False if failed

        """
        try:
            data = self.fetch_data()
            df = self.parse_data(data=data)
            self.save_data(df=df)
            logger.info("[✓] Fetched, parsed and saved for %s", self.table_name)
            return True

        except requests.exceptions.RequestException as e:
            logger.error("Error")
            return False

        except Exception as e:
            logger.error("Error")
            return False


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAST_UPDATED_TIME = datetime.now()

crime_rate_fetcher = Fetcher(
    api_url=
    'https://pxdata.stat.fi:443/PxWeb/api/v1/en/StatFin/rpk/statfin_rpk_pxt_13it.px',
    query_parameters_file=os.path.join(BASE_DIR, "config", "crime_rate.json"),
    db_name=os.path.join(BASE_DIR, "db", "combined_db.sqlite3"),
    table_name='crime_rate',
    area_path='Kunta',
    description_path='Rikosryhmä ja teonkuvauksen tarkenne',
    timeframe_path='Kuukausi',
    age_path='',
    combinations_order=['timeframe', 'area', 'description'],
    columns=['id', 'area', 'timeframe', 'description', 'value', 'last_updated'],
)

demographics_fetcher = Fetcher(
    api_url=
    'https://pxdata.stat.fi:443/PxWeb/api/v1/en/StatFin/vaerak/statfin_vaerak_pxt_11ra.px',
    query_parameters_file=os.path.join(BASE_DIR, "config", "demographics.json"),
    db_name=os.path.join(BASE_DIR, "db", "combined_db.sqlite3"),
    table_name='demographics',
    area_path='Alue',
    description_path='Tiedot',
    timeframe_path='',
    age_path='',
    combinations_order=['area', 'description'],
    columns=['id', 'area', 'description', 'value', 'last_updated'],
)

education_fetcher = Fetcher(
    api_url=
    'https://pxdata.stat.fi:443/PxWeb/api/v1/en/StatFin/vkour/statfin_vkour_pxt_12bq.px',
    query_parameters_file=os.path.join(BASE_DIR, "config", "education.json"),
    db_name=os.path.join(BASE_DIR, "db", "combined_db.sqlite3"),
    table_name='education',
    area_path='Alue',
    description_path='Koulutusaste',
    timeframe_path='',
    age_path='Ikä',
    combinations_order=['area', 'age', 'description'],
    columns=['id', 'area', 'age', 'description', 'value', 'last_updated'],
)

unemployment_fetcher = Fetcher(
    api_url=
    'https://pxdata.stat.fi:443/PxWeb/api/v1/en/StatFin/tyonv/statfin_tyonv_pxt_12r5.px',
    query_parameters_file=os.path.join(BASE_DIR, "config",
                                       "employment_rate.json"),
    db_name=os.path.join(BASE_DIR, "db", "combined_db.sqlite3"),
    table_name='employment_rate',
    area_path='Alue',
    description_path='Tiedot',
    timeframe_path='Kuukausi',
    age_path='',
    combinations_order=['area', 'timeframe', 'description'],
    columns=['id', 'area', 'timeframe', 'description', 'value', 'last_updated'],
)

income_fetcher = Fetcher(
    api_url=
    'https://pxdata.stat.fi:443/PxWeb/api/v1/en/StatFin/tjt/statfin_tjt_pxt_118w.px',
    query_parameters_file=os.path.join(BASE_DIR, "config", "income.json"),
    db_name=os.path.join(BASE_DIR, "db", "combined_db.sqlite3"),
    table_name='income',
    area_path='Alue',
    description_path='Tiedot',
    timeframe_path='',
    age_path='',
    combinations_order=['description', 'area'],
    columns=['id', 'area', 'description', 'value', 'last_updated'],
)

traffic_fetchers = Fetcher(
    api_url=
    'https://pxdata.stat.fi:443/PxWeb/api/v1/en/StatFin/ton/statfin_ton_pxt_12qh.px',
    query_parameters_file=os.path.join(BASE_DIR, "config",
                                       "traffic_accidents.json"),
    db_name=os.path.join(BASE_DIR, "db", "combined_db.sqlite3"),
    table_name='traffic_accidents',
    area_path='Alue',
    description_path='Tiedot',
    timeframe_path='Vuosi',
    age_path='',
    combinations_order=['area', 'timeframe', 'description'],
    columns=['id', 'area', 'timeframe', 'description', 'value', 'last_updated'],
)


def run_all_fetchers():
    """

    Returns:
        None: This function does not return a value

    """
    fetchers = [("Crime rate fetcher", crime_rate_fetcher),
                ("Demographics fetcher", demographics_fetcher),
                ("Education fetcher", education_fetcher),
                ("Income fetcher", income_fetcher),
                ("Unemployment fetcher", unemployment_fetcher),
                ("Traffic accidents fetcher", traffic_fetchers)]

    res = {}
    for name, fetcher in fetchers:
        try:
            success = fetcher.fetch_parse_save()
            res[name] = success

            if success:
                logger.info("[✓] Fetcher %s completed successfully\n\n", name)
            else:
                logger.warning("Fetcher %s failed", name)

        except Exception as e:
            res[name] = False
            print("Error")

    successful_fetchers = sum(1 for s in res.values() if s)
    p = "█" * successful_fetchers + "-" * (len(fetchers) - successful_fetchers)
    logger.info(f"\n{'-' * 50}\nAll fetchers completed. [{p}] {successful_fetchers}/{len(fetchers)} \n{'-' * 50}")


if __name__ == "__main__":
    run_all_fetchers()
