import pandas as pd
from .table_splitter import TableSplitter

class VtbSplitter(TableSplitter):
    def split(
        self, 
        excel_path:str,
        ):
        df = pd.read_excel(
            excel_path, 
            sheet_name="brokerage_report", 
            header=None
            )
        df_dict = {}
        current_table = []
        for index, row in df.iterrows():
            if row.isna().all():
                if current_table:
                    df = pd.DataFrame(current_table)
                    df_cleaned = df.dropna(axis=1, how='all')
                    table_name = df_cleaned.iloc[0, 0]
                    df_dict[table_name] = df_cleaned
                    current_table = []
            else:
                current_table.append(row.values)
        if current_table:
            df = pd.DataFrame(current_table)
            df_cleaned = df.dropna(axis=1, how='all')
            table_name = df_cleaned.iloc[0, 0]
            df_dict[table_name] = df_cleaned
        self.df_dict = df_dict
        return df_dict
    
if __name__ == '__main__':
    splitter = VtbSplitter()
    dict = splitter.split(r'./.reports/vtb20250818_20250821.xlsx')
    splitter.save_excel(r'./.output/vtb_splitter.xlsx')
    for key in dict.keys():
        print(key)