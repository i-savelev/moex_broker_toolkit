import pandas as pd
from .report_strategy import ReportStrategy
from .target_allocator import TargetAllocator
from pathlib import Path
import datetime

class MdReportStrategy(ReportStrategy):
    """
    Стратегия генерации отчета в формате Markdown.
    Преобразует DataFrame в читаемую Markdown-таблицу с заголовком.
    """

    def __init__(
            self,
            targetAllocator: TargetAllocator,
            template_path:str
            ) -> None:
        """
        Инициализирует стратегию с заголовком отчета.
        :param title: Заголовок отчета, по умолчанию "Отчет".
        """
        self.targetAllocator = targetAllocator
        self._template = self._load_template(template_path)

    def _load_template(self, path: str) -> str:
        """Загружает содержимое шаблона из файла.
        :param path: Путь к файлу шаблона.
        :returns: Содержимое шаблона как строка.
        :raises FileNotFoundError: Если файл не существует.
        :raises ValueError: Если файл пуст.
        """
        template_path = Path(path)
        if not template_path.exists():
            raise FileNotFoundError(f"Шаблон не найден по пути: {template_path}")
        content = template_path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError("Файл шаблона пуст.")
        return content

    def generate(self) -> str:
        """
        Генерирует Markdown-отчет из DataFrame.
        :param data: Данные для генерации отчета.
        :returns: Отчет в формате Markdown.
        :raises TypeError: Если data не является экземпляром pd.DataFrame.
        """
        deposit = self.targetAllocator.deposit
        distribution_table = self.distrib_of_money_table()
        distribution_string = self.distrib_of_money_string(distribution_table)
        date = datetime.date.today()
        context = {
            "deposit": deposit,
            "distribution_table": distribution_table.to_markdown(index=False),
            "distribution_string": distribution_string,
            "date": date
        }

        try:
            return self._template.format_map(context)
        except KeyError as e:
            raise ValueError(f"В шаблоне отсутствует переменная: {e}")
        except Exception as e:
            raise ValueError(f"Ошибка при форматировании шаблона: {e}")

        
    def distrib_of_money_table(self):
        df = self.targetAllocator.AllocationTable[
                [
                'ticker', 
                'delt (лот)_calc',
                'delt расчет_calc',
                '%_source',
                '%_target',
                '%_calc'
                ]
            ]
        df = df.rename(columns={
                'delt (лот)_calc':'lot number',
                }
            )
        
        df['buy/sell'] = df.apply(self.sell_buy_string, axis = 1)
        df = df[
            [
                'ticker',
                'buy/sell',
                '%_source',
                '%_target',
                '%_calc'
                ]
            ]
        return df
    
    @staticmethod
    def sell_buy_string(row):
        if row['lot number'] > 0:
            return f'buy {round(row['lot number'])} шт. ({round(row['delt расчет_calc'])} руб.)'
        elif row['lot number'] < 0:
            return f'sell {abs(round(row['lot number']))} шт. ({round(row['delt расчет_calc'])} руб.)'
        else: return '-'

    def distrib_of_money_string(self, df:pd.DataFrame):
        df = df[df['buy/sell'] != '-']
        string = ''
        for idx in df.index:
            string += f'{df.loc[idx, 'ticker']}: {df.loc[idx, 'buy/sell']}\n'
        return string