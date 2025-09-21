from .report_strategy import ReportStrategy
import pandas as pd
from pathlib import Path


class ReportGenerator:
    """Генератор отчетов, использующий стратегию форматирования.
    Разделяет логику получения данных и их представления.
    """

    def __init__(self, strategy: ReportStrategy) -> None:
        """Инициализирует генератор с заданной стратегией.
        :param strategy: Стратегия форматирования отчета.
        :raises TypeError: Если strategy не реализует ReportStrategy.
        """
        if not isinstance(strategy, ReportStrategy):
            raise TypeError("Стратегия должна быть экземпляром ReportStrategy.")
        self._strategy = strategy
        self.report:str = ''

    def generate_report(self) -> str:
        """Генерирует отчет с использованием текущей стратегии.
        :param  Данные для генерации отчета.
        :returns: Сформированный отчет в виде строки.
        :raises TypeError: Если data не является pd.DataFrame.
        """
        self.report = self._strategy.generate()
        return self.report

    def set_strategy(self, strategy: ReportStrategy) -> None:
        """Изменяет стратегию форматирования отчета.
        :param strategy: Новая стратегия.
        :raises TypeError: Если strategy не реализует ReportStrategy.
        """
        if not isinstance(strategy, ReportStrategy):
            raise TypeError("Стратегия должна быть экземпляром ReportStrategy.")
        self._strategy = strategy

    def save_report(self, path:str):
        """Сохраняет последний сгенерированный отчет в файл.
        Если отчет еще не был сгенерирован — выбрасывает исключение.
        :param path: Путь к файлу, куда нужно сохранить отчет.
        :raises ValueError: Если отчет еще не был сгенерирован.
        :raises OSError: Если возникла ошибка при записи файла (например, нет прав, диск переполнен).
        :raises TypeError: Если path не является строкой.
        """
        if not isinstance(path, str):
            raise TypeError("Путь к файлу должен быть строкой.")

        if self.report is None:
            raise ValueError(
                "Отчет еще не был сгенерирован. Вызовите generate_report() перед save_report()."
            )

        file_path = Path(path)
        try:
            # Создаем родительские директории, если их нет
            # file_path.parent.mkdir(parents=True, exist_ok=True)
            # # Записываем отчет в файл
            file_path.write_text(self.report, encoding="utf-8")
        except OSError as e:
            raise OSError(f"Не удалось сохранить отчет по пути '{path}': {e}") from e
