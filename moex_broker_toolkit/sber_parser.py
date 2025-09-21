import pandas as pd
from .broker_parser import BrokerParser

class SberPareser(BrokerParser): 
    def get_source_df(self)->pd.DataFrame:
        df: pd.DataFrame = self.split_tables_dict[2]
        df.columns = df.iloc[0]
        df = df[
                [
                'Основной рынок',
                'Плановые показатели'
                ]
            ]
        df.columns = df.iloc[1]
        df = df.iloc[4:-3].reset_index(drop=True)
        df = df.rename(columns=self.RENAME_DICT_SBER)
        df['Кол-во (шт)'] = df['Плановый исходящий остаток, шт'].str.replace(' ', '').astype(float)
        df = df[self.COLUMNS_TO_KEEP]
        return df

    RENAME_DICT_SBER = {
        'ISIN ценной бумаги': 'ISIN',
        'Количество, шт': 'Кол-во (шт)',
        }