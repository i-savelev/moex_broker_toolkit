import pandas as pd
from typing import Optional
from .all_stock_info import AllStockInfo


class DistributionTable:
    def __init__(
            self,
            file_path,
            all_stock_info: AllStockInfo,
            ):
        self.file_path = file_path
        self.df_dict:dict[str, pd.DataFrame]
        self.distribution_table:pd.DataFrame
        self.all_stock_df = all_stock_info.all_stock_df

    def _get_df_dict(self) -> dict[str, pd.DataFrame]:
        df_dict = pd.read_excel(
            io=self.file_path,
            sheet_name=None,
        )
        for key in df_dict:
            if key == 'categories':
                df_dict[key].dropna(subset=['category'], inplace=True)
                self.percent_error(
                    df_dict[key],
                    100,
                    '%',
                    key
                )
            else:
                df_dict[key].dropna(subset=['ticker'], inplace=True)
                self.percent_error(
                    df_dict[key],
                    100,
                    '%',
                    key
                )
        self.df_dict = df_dict
        return df_dict
    
    @staticmethod
    def percent_error(df:pd.DataFrame, val: float, column:str, name:str):
        sum = df[column].sum()
        if sum != val:
            raise ValueError(f'сумма процентов {name} равна {sum}, а не равно 100%')

    def get_table(self):
        self._get_df_dict()
        categories_df = self.df_dict['categories']
        categories_list = categories_df['category'].tolist()
        df_list:list[pd.DataFrame] = []
        for key in self.df_dict:
            if key != 'categories':
                if key in categories_list:
                    df:pd.DataFrame = self.df_dict[key]
                    percent = categories_df.loc[
                        categories_df['category'] == key, 
                        '%'
                        ].iloc[0]
                    df_copy = df.copy()
                    df_copy['%'] = percent/100*df['%'].round(10)
                    df_copy['category'] = key
                    df_list.append(df_copy)
                else: raise Exception(f'листа {key} нет в категориях')
        self.distribution_table = pd.concat(df_list).reset_index(drop=True)
        for index, row,  in self.distribution_table.iterrows():
            id = row['ticker']
            isin = self.all_stock_df.loc[
                self.all_stock_df['SECID'] == id, 
                'ISIN'
                ].iloc[0]
            lot_size = self.all_stock_df.loc[
                self.all_stock_df['SECID'] == id, 
                'LOTSIZE'
                ].iloc[0]
            shortname = self.all_stock_df.loc[
                self.all_stock_df['SECID'] == id, 
                'SHORTNAME'
                ].iloc[0]
            self.distribution_table.at[index, "ISIN"] = isin
            self.distribution_table.at[index, "Размер лота"] = lot_size
            self.distribution_table.at[index, "name"] = shortname
        self.distribution_table["Размер лота"] = self.distribution_table["Размер лота"].astype('float')
        return self.distribution_table

    
if __name__ == '__main__':
    ds = DistributionTable(r'./.support_files/index_fund.xlsx')
    d = ds._get_df_dict()
    print(ds.get_table())