from .company import Company
import re
import pathlib
import pandas as pd

class FinProcessor():
    def __init__(self):
        pass
    
    @staticmethod
    def extract_ticker(name: str) -> str:
        match = re.search(r'\(([^)]+)\)', name)
        return match.group(1) if match else None
    
    @staticmethod
    def by_ticker(folder_path:str, ticker:str)->Company|None:    
        company = None
        folder = pathlib.Path(folder_path)
        files = folder.glob('*.csv')
        for file in files: 
            _ticker = FinProcessor.extract_ticker(file.name)
            if ticker.lower() == _ticker.lower():
                company = Company.from_csv(file)
        return company
            
    @staticmethod
    def rating_df(folder_path, ir_rating:pd.DataFrame, n:int):
        data = []
        folder = pathlib.Path(folder_path)
        files = folder.glob('*.csv')
        for file in files:
            score = 0
            com = Company.from_csv(file)
            ir_score = com.ir_score(ir_rating)
            profit_score = com.grow_score('Чистая прибыль, млрд руб', n)
            div_count_score = com.count_score('Див.выплата, млрд руб', n)
            div_grow_score = com.grow_score('Див.выплата, млрд руб', n)
            cap = com.cap()
            if ir_score is None:
                score = (profit_score + div_count_score+ div_grow_score)/3
            else:
                score = (ir_score + profit_score + div_count_score+ div_grow_score)/4
            row = {
                'ticker':com.ticker,
                'name': com.name,
                'ir_score':ir_score,
                'profit_score':profit_score,
                'div_count_score':div_count_score,
                'div_grow_score':div_grow_score,
                'score':round(score, 2),
                'cap':cap,
                }
            data.append(row)
        return pd.DataFrame(data).set_index('ticker')