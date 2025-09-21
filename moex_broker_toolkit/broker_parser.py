from typing import Optional
import pandas as pd
from .all_stock_info import AllStockInfo
from .table_splitter import TableSplitter
from .report_registry import ReportRegistry 


class BrokerParser:
    def __init__(
            self, 
            all_stock_info: AllStockInfo,
            splitter: TableSplitter,
            registry: ReportRegistry
            ) -> None:
        self.all_stock_df = all_stock_info.all_stock_df
        self.split_tables_dict: dict[str, pd.DataFrame] = splitter.df_dict
        self.balance_report: pd.DataFrame
        self.registry = registry

    def get_balance_report_df(self) -> pd.DataFrame:
        df:pd.DataFrame = self.get_source_df()
        for index, row,  in df.iterrows():
            isin = row['ISIN']
            ticker = self.all_stock_df.loc[
                self.all_stock_df['ISIN'] == isin, 
                'SECID'
                ].iloc[0]
            lot_size = self.all_stock_df.loc[
                self.all_stock_df['ISIN'] == isin, 
                'LOTSIZE'
                ].iloc[0]
            shortname = self.all_stock_df.loc[
                self.all_stock_df['ISIN'] == isin, 
                'SHORTNAME'
                ].iloc[0]
            df.at[index, "ticker"] = ticker
            df.at[index, "Размер лота"] = lot_size
            df.at[index, "name"] = shortname

        # df['Стоимость'] = df['Стоимость'].astype('float')
        df["Размер лота"] = df["Размер лота"].astype('float')
        df['Кол-во (шт)'] = df['Кол-во (шт)'].astype('float')
        self.balance_report = df
                
        if self.registry and self.balance_report is not None:
            self.registry.add(self.balance_report)
        return df
    
    def get_source_df(self) -> pd.DataFrame:
        return pd.DataFrame()
    
    COLUMNS_TO_KEEP = [
        'ISIN',
        'Кол-во (шт)',
        ]
        