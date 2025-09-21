from .report_registry import ReportRegistry
import pandas as pd
from . import moex_api_utils as moex
from typing import Optional
from .distribution_table import DistributionTable

class BalanceReport:
    def __init__(
            self,
            report_registry: ReportRegistry,
            distribution_table: DistributionTable,

            ):
        self.report_registry = report_registry
        self.balance_report: pd.DataFrame 
        self.dt: DistributionTable = distribution_table

    def get_balance_report(self) -> pd.DataFrame:
        balance_report_from_broker = pd.concat(
            self.report_registry.report_list, 
            ignore_index=True
            )
        balance_report = pd.concat(
            [balance_report_from_broker, self.dt.distribution_table], 
            ignore_index=True
            )
        balance_report = balance_report.groupby('ticker', as_index=False).agg(
            {
            'name': 'first',
            'Кол-во (шт)': 'sum',
            'Размер лота': 'first'
            }
        ) 
        balance_report['Цена'] = balance_report.apply(self.get_price, axis = 1)
        balance_report['Стоимость'] = (
            balance_report['Цена']
            *balance_report['Кол-во (шт)']
            )
        balance_report['%'] = round(
            balance_report['Стоимость']/balance_report['Стоимость']
            .sum()*100, 2)
        self.balance_report = balance_report
        return balance_report
    
    @staticmethod
    def get_price(row):
        ticker = row['ticker']
        price = moex.get_last_price(ticker=ticker)
        return price