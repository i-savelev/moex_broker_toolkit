import pandas as pd
from typing import Optional

class TableSplitter:
    def __init__(self):
        self.df_dict: dict[str, pd.DataFrame] = {}

    def split(self) -> dict[str, pd.DataFrame]:
        return {}
    
    def save_excel(
            self,
            output_path:str
        ) -> None:
        if self.df_dict is not None:
            with pd.ExcelWriter(
                output_path, 
                mode='w', 
                engine='openpyxl'
                ) as writer:
                for i, key in enumerate(self.df_dict):
                    self.df_dict[key].to_excel(
                        writer, 
                        sheet_name=f'{i}', 
                        index=False
                        )
        else: print('empty dataframe dict')
    
if __name__ == '__main__':
    tb = TableSplitter()
    tb.save_excel(r'../.output/test.xlsx')