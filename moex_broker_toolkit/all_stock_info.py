import pandas as pd


class AllStockInfo:
    def __init__(
            self, 
            path:str
            ):
        self.all_stock_df = self.get_all_stock_df(path)

    def get_all_stock_df(
            self, 
            path_csv:str
            ) -> pd.DataFrame:
        source_df = pd.read_csv(
            path_csv, 
            header=None,
            encoding='utf-8', 
            sep=';'
            )
        header = source_df.iloc[2]
        source_df.columns = header
        source_df.drop([0, 1, 2], axis = 0, inplace=True)
        df = source_df.reset_index(drop=True)
        df = pd.DataFrame(df)
        self.all_stock_df = df
        return df