import pandas as pd
from .table_splitter import TableSplitter
from io import StringIO


class SberSplitter(TableSplitter):
    def split(
            self,
            html_path:str
        ) -> dict[str, pd.DataFrame]:
        df_dict = {}
        html_content = None
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        tables = pd.read_html(StringIO(html_content))
        for i, table in enumerate(tables):
            df_dict[i] = table
        self.df_dict = df_dict
        return df_dict
    
if __name__ == '__main__':
    splitter = SberSplitter()
    splitter.split(r'./.reports/400LSUS_11082025.html')
    splitter.save_excel(r'./.output/sber_splitter.xlsx')
