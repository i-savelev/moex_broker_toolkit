import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import re
from .ir_rating import IRrating


class Company():
    '''

    '''
    def __init__(self, df:pd.DataFrame, ticker, name) -> None:
        self.ticker = ticker
        self.name = name
        self.df = df
        
    @staticmethod    
    def from_csv(path:str):
        file = pathlib.Path(path)
        df = pd.read_csv(path, sep=';', index_col=0, encoding='utf-8')

        def _clean_value(x):
            if pd.isna(x):
                return np.nan
            x_str = str(x).strip()
            if x_str.lower() in ['nan', 'none', '']:
                return np.nan
            x_str = x_str.replace(' ', '').replace(',', '.').replace('%', '')
            try:
                return float(x_str)
            except ValueError:
                return np.nan
        def _is_year_label(label):
            try:
                int(label)
                return True
            except (ValueError, TypeError):
                return False

        def _extract_ticker(name: str) -> str:
            match = re.search(r'\(([^)]+)\)', name)
            return match.group(1) if match else None
         
        year_mask = df.columns.map(_is_year_label)
        columns_to_ceep = df.columns[year_mask]
        df = df.map(_clean_value)
        df = df[columns_to_ceep]
        df = df.dropna(how='all')
        ticker = _extract_ticker(file.name)
        return Company(df=df, ticker=ticker, name=file.stem)
    
    @staticmethod
    def _add_figure_watermark(
            fig, 
            text='@ваш_канал', 
            position='bottom-right', 
            fontsize=7, 
            color='gray', 
            alpha=0.8
            ):
        pos_map = {
            'bottom-right': (0.98, 0.02, 'right', 'bottom'),
            'bottom-left':  (0.02, 0.02, 'left',  'bottom'),
            'top-right':    (0.95, 0.95, 'right', 'top'),
            'top-left':     (0.02, 0.98, 'left',  'top'),
        }
        
        if position not in pos_map:
            raise ValueError(f"Недопустимая позиция: {position}. Варианты: {list(pos_map.keys())}")
        
        x, y, ha, va = pos_map[position]
        
        fig.text(
            x, y,
            text,
            transform=fig.transFigure,
            fontsize=fontsize,
            ha=ha,
            va=va,
            color=color,
            alpha=alpha
        )

    def plot_one_chart(self, title, window=3, axes=None, show:bool=True):
        row:pd.Series = self.df.loc[title].copy()
        row =  row.dropna()
        ax = row.plot(
            kind='bar',
            ax=axes,
            color="#182645",
            alpha=0.8,
            width=0.8,
            fontsize=12
            )

            # --- Скользящая средняя ТОЛЬКО по годам ---
        if len(row.dropna()) >= window:
            rolling = row.rolling(window=window, min_periods=1).mean()
            # Наносим линию только на позиции годов
            year_positions = [i for i, label in enumerate(row.index)]
            ax.plot(
                year_positions,
                rolling,
                color="#D96060",
                linewidth=1,
                marker='o',
                markersize=3,
                label=f'Скольз. ср. ({window})'
            )
            ax.legend(fontsize=7)

        # --- Подписи значений ---
        for container in ax.containers:
            labels = []
            for v in container.datavalues:
                if v <10: labels.append(f'{v:.1f}' if pd.notna(v) else '')
                else: labels.append(f'{v:.0f}' if pd.notna(v) else '')

            ax.bar_label(
                container,
                labels,
                padding=2,
                fontsize=7
                )

        # --- Настройка оси Y с отступами ---
        valid_vals = row.dropna()
        if len(valid_vals) > 0:
            y_min = valid_vals.min()
            y_max = valid_vals.max()
            y_range = y_max - y_min if y_max != y_min else max(abs(y_max), 1)
            margin = y_range * 0.2
            ax.set_ylim(
                y_min - (margin if y_min >= 0 else margin * 1.5),
                y_max + margin
            )
        else:
            ax.set_ylim(0, 1)

        ax.set_title(title, fontsize=10)
        ax.grid(False)
        ax.tick_params(axis='x', labelsize=7, rotation=45)
        ax.tick_params(axis='y', labelsize=7)
        if show: plt.show()
        return ax

    def plot_multiple_chart(
            self,
            metric_list:list[str], 
            window:int=3, 
            rows:int=3, 
            cols:int= 2, 
            figsize = (12, 9.5)
            ):
        df =  self.df
        main_title = self.name
        fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=figsize)
        fig.suptitle(main_title, fontsize=25, fontweight='black', y = 0.95)
        axes = axes.flatten()
        plot_idx = 0

        for param in df.index:
            if param not in metric_list:
                continue
            if plot_idx >= len(axes):
                break

            self.plot_one_chart(
                title=param,
                window=window,
                axes=axes[plot_idx],
                show=False
                )
            plot_idx += 1

        for j in range(plot_idx, len(axes)):
            axes[j].set_visible(False)
        plt.tight_layout(rect=(0, 0, 1, 0.95))
        self._add_figure_watermark(
            fig=fig,
            text='@one_investor_fund',
            position='top-right',
            fontsize=14,
            color='gray'
        )
        plt.show()

    def get_metric_list(self):
        return self.df.index
    
    def _processed_data(self, metric:str, n:int) -> pd.Series:
        n = n+1
        last_n:pd.Series = None
        if metric in self.df.index:
            s:pd.Series = self.df.loc[metric]
            s_clean = pd.to_numeric(s, errors='coerce').fillna(0)
            last_n = s_clean.iloc[-n:]
            if len(last_n) < n:
                missing = n - len(last_n)
                padding = pd.Series([0.0] * missing)
                last_n = pd.concat([padding, last_n]).iloc[-n:]
        return last_n
        

    def grow_score(self, metric:str, n:int):
        s = self._processed_data(metric, n)
        if s is None:
            return 0
        l = s.values.tolist()
        l.reverse()
        score = 0
        val = 0
        for i, value in enumerate(l):
            if i >= len(l)-1: break
            if (value > l[i+1]) and (value > 0):
                val += 1
            if (value < 0):
                val -= 1
        score = val/n
        return round(score, 2)

    def count_score(self, metric:str, n:int):
        s = self._processed_data(metric, n)
        if s is None:
            return 0
        l = s.values.tolist()
        l.reverse()
        score = 0
        val = 0
        for i, value in enumerate(l):
            if i >= len(l)-1: break
            if value > 0:
                val += 1
        score = val/n
        return round(score, 2)
    
    def ir_score(self, ir_rating:pd.DataFrame):
        df = ir_rating.set_index('ticker')
        if self.ticker in df.index:
            rating = df.loc[self.ticker]['rating']
            return rating/100
        else: return None


    def cap(self):
        cap = self.df.loc["Капитализация, млрд руб"].iloc[-1]
        return cap

    METRIC_LIST = [
        'Выручка, млрд руб',
        'Чистая прибыль, млрд руб',
        'Чистый долг, млрд руб',
        'Долг/EBITDA',
        'Див.выплата, млрд руб',
        'Див доход, ао, %',
    ]

if __name__ == '__main__':
    folder = pathlib.Path(r'.finance_reports')

    tickers = [
        'RTKM',
    ]

    com = Company.from_csv('.finance_reports/X5 (X5).csv')
    com.df
    com.name
    com.ticker
    com.plot_multiple_chart(Company.METRIC_LIST)
    print(com.get_metric_list(), com.df, com.name, com.ticker)
    print(com.count_score('Див.выплата, млрд руб', 7))
    print(com._processed_data('Див.выплата, млрд руб', 7))
    com.plot_one_chart('Див.выплата, млрд руб')
