import pandas as pd
from .broker_parser import BrokerParser

class VtbPareser(BrokerParser): 
    def get_source_df(self)->pd.DataFrame:
        source_df = self.split_tables_dict['Отчёт об остатках ценных бумаг']
        df = source_df.iloc[1:-1].reset_index(drop=True)
        df.columns = df.iloc[0]
        df = df[1:]
        df = df.reset_index(drop=True)
        df.columns = df.columns.str.replace('\n', ' ', regex=False)
        df = df[df['Плановый исходящий остаток (шт)']>0]
        first_col = df.columns[0]
        mask = ~(
            df[first_col].notna() &
            df[df.columns[1:]].isna().all(axis=1)
        )
        df = df[mask].copy()
        df = df.rename(columns=self.RENAME_DICT_VTB)
        df = df[self.COLUMNS_TO_KEEP]
        df['ISIN'] = df['ISIN'].apply(lambda s: s.split(', ')[2])
        return df

    RENAME_DICT_VTB = {
        'Наименование ценной бумаги, № гос. регистрации, ISIN': 'ISIN',
        'Плановый исходящий остаток (шт)': 'Кол-во (шт)', 
        }