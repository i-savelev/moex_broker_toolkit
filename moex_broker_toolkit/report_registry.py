import pandas as pd


class ReportRegistry:
    def __init__(self):
        self.report_list: list[pd.DataFrame] = list()
        
    def add(self, df):
        self.report_list.append(df)

