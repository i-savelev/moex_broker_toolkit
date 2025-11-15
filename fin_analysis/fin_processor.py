from .company import Company
import re
import pathlib

class FinProcessor():
    def __init__(self):
        pass
    
    @staticmethod
    def company_by_ticker(folder_path:str, ticker:str):
        company = None
        folder = pathlib.Path(folder_path)
        files = folder.glob('*.csv')
        for file in files: 
            _ticker = FinProcessor.extract_ticker(file.name)
            if ticker.lower() == _ticker.lower():
                company = Company.from_csv(file)
        return company
    
    @staticmethod
    def extract_ticker(name: str) -> str:
            match = re.search(r'\(([^)]+)\)', name)
            return match.group(1) if match else None
    
    def by_ticker():
         ...