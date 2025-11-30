import pandas as pd
from .distribution_table import DistributionTable
from .balance_report import BalanceReport
import numpy as np
from typing import Optional


class TargetAllocator:
    def __init__(
            self,
            balance_report: BalanceReport ,
            distribution_table: DistributionTable,
            deposit:float = 0,
            allow_sell:bool = False,
            tickers_to_sell:list[str] = []
            ):
        self.br: BalanceReport = balance_report
        self.dt: DistributionTable = distribution_table
        self.money_count:Optional[float] = None 
        self.AllocationTable: pd.DataFrame
        self.work_log:str = ''
        self.deposit:float = deposit
        self.allow_sell:bool = allow_sell
        self.tickers_to_sell:list[str] = tickers_to_sell
        
    def get_money_count(self):
        money_count = self.br.balance_report['Стоимость'].sum()
        self.money_count = money_count
        return money_count

    def get_distrib_of_money_df(self,) -> pd.DataFrame:
        money_count = self.get_money_count() + self.deposit
        df = self.dt.distribution_table.copy()
        df['Стоимость'] = (money_count*df['%']/100)
        df['Стоимость'] = df['Стоимость'].astype(float).round(1)
        merged_df = pd.merge(
            df, 
            self.br.balance_report, 
            on=['ticker', 'name', 'Размер лота'],
            suffixes=('_target', '_source'),
            how='outer'
            ).fillna(0)
        merged_df['delt (руб)'] = merged_df['Стоимость_target'] - merged_df['Стоимость_source']
        
        if not self.allow_sell:
            merged_df['delt (руб)'] = (
                merged_df['delt (руб)'].apply(lambda x: max(x, 0))
                )
        else:
            if self.tickers_to_sell:
                mask = (
                    (merged_df['delt (руб)'] < 0) 
                    & (~merged_df['ticker'].isin(self.tickers_to_sell))
                )
                merged_df.loc[mask, 'delt (руб)'] = 0

        merged_df['delt (лот)'] = (
            merged_df['delt (руб)']/merged_df['Цена']/merged_df['Размер лота']
            )
        merged_df['delt (лот)'] = (
            merged_df['delt (лот)']
            .apply(lambda x: np.ceil(x) if x < 0 else np.floor(x))
            )
        merged_df['delt расчет'] = (
            merged_df['delt (лот)']
            *merged_df['Размер лота']
            *merged_df['Цена']
            )
        merged_df = self._adjust_for_funds(deposit=self.deposit, df=merged_df)
        merged_df['Стоимость_calc'] = merged_df['Стоимость_source'] + merged_df['delt расчет_calc']
        merged_df['%_calc'] = round(merged_df['Стоимость_calc']/merged_df['Стоимость_calc'].sum()*100, 2)
        
        self.AllocationTable = merged_df
        return self.AllocationTable

    # def _adjust_for_funds(self, deposit:float, df: pd.DataFrame):
    #     sell_needed = abs(df[df['delt расчет'] < 0]['delt расчет'].sum())+deposit
    #     buy_needed = df[df['delt расчет'] > 0]['delt расчет'].sum()

    #     df['delt (лот)_calc'] = df['delt (лот)'].copy()
    #     df['delt расчет_calc'] = df['delt расчет'].copy()
    #     df = df.sort_values(['delt расчет'], ascending=[False])
    #     if buy_needed > sell_needed:
    #         self.work_log += f"\nПокупок больше. Уменьшение суммы покупок: sell={sell_needed}, buy={buy_needed}"
    #         remaining_sell = abs(sell_needed)
    #         for idx in df.index:
    #             if df.loc[idx, 'delt расчет'] > 0:
    #                 cost = abs(df.loc[idx, 'delt расчет'])
    #                 if cost <= remaining_sell:
    #                     remaining_sell -= cost
    #                 else:
    #                     lots = np.floor(remaining_sell / df.loc[idx, 'Цена'] / df.loc[idx, 'Размер лота'])
    #                     df.loc[idx, 'delt (лот)_calc'] = lots
    #                     df.loc[idx, 'delt расчет_calc'] = lots * df.loc[idx, 'Размер лота'] * df.loc[idx, 'Цена']
    #                     remaining_sell = 0
    #     elif sell_needed > buy_needed:
    #         self.work_log += f"\nПродаж больше. Уменьшение суммы продаж: sell={sell_needed}, buy={buy_needed}"
    #         remaining_buy = buy_needed - deposit
    #         for idx in df.index:
    #             if df.loc[idx, 'delt расчет'] < 0:
    #                 cost = abs(df.loc[idx, 'delt расчет'])
    #                 if cost <= remaining_buy:
    #                     remaining_buy -= cost
    #                 else:
    #                     lots = np.floor(remaining_buy / df.loc[idx, 'Цена'] / df.loc[idx, 'Размер лота'])
    #                     df.loc[idx, 'delt (лот)_calc'] = -lots
    #                     df.loc[idx, 'delt расчет_calc'] = -lots * df.loc[idx, 'Размер лота'] * df.loc[idx, 'Цена']
    #                     remaining_buy = 0
    #     self.work_log += f'\ndelta = {df['delt расчет_calc'].sum()}'
    #     return df

    def _adjust_for_funds(self, deposit: float, df: pd.DataFrame):
        sell_needed = abs(df[df['delt расчет'] < 0]['delt расчет'].sum())
        available_funds = sell_needed + deposit
        buy_orders = df[df['delt расчет'] > 0].copy()

        # Инициализация расчётных столбцов
        df['delt (лот)_calc'] = df['delt (лот)'].copy()
        df['delt расчет_calc'] = df['delt расчет'].copy()

        # Если нечего покупать, выходим
        if buy_orders.empty:
            self.work_log += f"\nНет покупок. Доступно: {available_funds}"
            return df

        # Считаем стоимость одного лота
        buy_orders['cost_per_lot'] = buy_orders['Цена'] * buy_orders['Размер лота']
        
        # Сортируем по возрастанию стоимости лота — сначала дешёвые
        buy_orders = buy_orders.sort_values('cost_per_lot')

        remaining_funds = available_funds
        total_spent = 0

        for idx in buy_orders.index:
            cost_per_lot = buy_orders.loc[idx, 'cost_per_lot']
            max_lots_by_target = int(buy_orders.loc[idx, 'delt (лот)'])  # целевое количество лотов

            # Сколько лотов можем реально купить
            affordable_lots = min(max_lots_by_target, int(remaining_funds // cost_per_lot))

            actual_cost = affordable_lots * cost_per_lot

            df.loc[idx, 'delt (лот)_calc'] = affordable_lots
            df.loc[idx, 'delt расчет_calc'] = actual_cost

            remaining_funds -= actual_cost
            total_spent += actual_cost

        # Обнуляем те, что не вошли (на случай, если были нецелые расчёты)
        for idx in df[~df.index.isin(buy_orders.index)].index:
            if df.loc[idx, 'delt расчет'] > 0:
                df.loc[idx, 'delt (лот)_calc'] = 0
                df.loc[idx, 'delt расчет_calc'] = 0

        self.work_log += f"\nБюджет на покупки: {available_funds:.0f}, потрачено: {total_spent:.0f}, остаток: {remaining_funds:.0f}"
        self.work_log += f'\nИтоговая дельта: {df["delt расчет_calc"].sum():.0f}'

        return df