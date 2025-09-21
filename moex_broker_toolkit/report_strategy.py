from abc import ABC, abstractmethod
import pandas as pd

class ReportStrategy(ABC):
    """
    Абстрактная стратегия генерации отчета.
    Определяет интерфейс для всех конкретных стратегий форматирования отчетов.
    """

    @abstractmethod
    def generate(self) -> str:
        """
        Генерирует отчет на основе переданного DataFrame.
        :param data: Данные для генерации отчета.
        :returns: Строка с отформатированным отчетом.
        :raises TypeError: Если data не является экземпляром pd.DataFrame.
        """
        pass