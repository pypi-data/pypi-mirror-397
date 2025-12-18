"""Модуль расширенного логгера с поддержкой Rich форматирования.

Основной класс Log предоставляет динамические методы логирования
с цветным выводом и табличным форматированием.
"""

import decimal
import inspect
import logging
import re
from collections import deque
from collections.abc import Callable
from datetime import datetime
from functools import lru_cache
from types import FrameType
from typing import Any

from rich.console import Console
from rich.table import Table

from logrich.config import config_main, console, console_dict, get_main_config, get_style


@lru_cache
class Log:
    """Расширенный логгер с поддержкой Rich форматирования.

    Класс предоставляет динамические методы логирования через __getattr__,
    позволяя вызывать log.любое_слово() для создания цветных логов.
    Поддерживает табличный вывод с информацией о файле и строке.

    Attributes:
        deque: Очередь для хранения имен уровней логирования
        config: Конфигурация логгера
    """

    def __init__(
        self,
        config: config_main,
        **kwargs: Any,
    ) -> None:
        """Инициализация логгера.

        Args:
            config: Конфигурация логгера с настройками отображения
            **kwargs: Дополнительные атрибуты для установки в экземпляр
        """
        # Очередь для хранения имен методов логирования
        self.deque: deque[str] = deque()
        # Конфигурация с настройками ширины, цветов и шаблонов
        self.config = config
        # Установка дополнительных атрибутов
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def print(
        self,
        *args: Any,  # вызов логгера без параметров выведет текущую дату
        frame: FrameType | None = None,
        **kwargs: Any,
    ) -> None:
        """Основной метод вывода логов с Rich форматированием.

        Обрабатывает различные типы сообщений и выводит их в табличном формате
        с информацией о файле, строке и уровне логирования.

        Args:
            *args: Сообщения для логирования. Если пусто - выводит текущее время
            frame: Фрейм стека для получения информации о вызове
            **kwargs: Дополнительные параметры (title, file_name, line)
        """

        # Проверка включен ли логгер в конфигурации
        if not self.config.LGR_LOGRICH_ON:
            return

        try:
            # Определение сообщения для вывода
            msg: Any | str | tuple[Any, ...]
            if args and len(args) == 1:
                # Одиночный аргумент
                msg = args[0]
            elif not args:
                # Без аргументов - выводим текущее время
                msg = datetime.now().strftime("%H:%M:%S")
            else:
                # Множественные аргументы - выводим как кортеж
                msg = args

            # Получение уровня логирования из очереди
            if not (level := self.deque.pop()):
                return

            # Формирование ключа для поиска стиля в конфигурации
            level_key: str = f"LOG_LEVEL_{level.upper()}_TPL"
            # Получение стиля оформления для данного уровня
            level_style: str = get_style(level_key)

            # если стиль определяется как пустая строка, то вывода не будет
            if not level_style:
                return

            # Получение фрейма стека для определения места вызова
            # Фрейм может быть передан извне или получен автоматически
            frame = frame or inspect.currentframe()

            # Переход к родительскому фрейму (место реального вызова)
            if isinstance(frame, FrameType):
                frame = frame.f_back

            # Проверка корректности фрейма
            if not frame:
                logging.warning("Frame undefined")
                return

            # Извлечение информации о месте вызова
            len_file_name_section: int = self.config.LGR_LEN_FILE_NAME_SECTION
            # Обрезка имени файла до заданной длины
            file_name: str = kwargs.get("file_name", frame.f_code.co_filename)[-len_file_name_section:]
            # Номер строки в файле
            line: int = kwargs.get("line", frame.f_lineno)
            # Расчет длины разделителя для заголовка
            divider: int = self.config.LGR_CONSOLE_WITH - len_file_name_section - self.config.LGR_REDUCE_DEVIDER_LEN
            # Заголовок сообщения (по умолчанию - линия из тире)
            title: str = kwargs.get("title", "-" * divider)

            # Обработка различных типов сообщений
            if isinstance(msg, str | int | float | bool | type(decimal) | type(None)):
                # Простые типы - выводим как строку в одной строке
                self.print_tbl(
                    message=str(msg),
                    file=file_name,
                    line=line,
                    level=level,
                    level_style=level_style,
                )
            elif isinstance(msg, (dict | tuple | list)):
                # Сложные объекты - выводим заголовок и отдельно объект
                # TODO: добавить специальное форматирование для dict, tuple, list
                self.print_tbl(
                    message=title,
                    file=file_name,
                    line=line,
                    level=level,
                    level_style=level_style,
                )
                # Форматированный вывод объекта в отдельной таблице
                self.format_extra_obj(message=msg)
            else:
                # Остальные типы - выводим как есть
                self.print_tbl(
                    message=msg,
                    file=file_name,
                    line=frame.f_lineno,
                    level=level,
                    level_style=level_style,
                )
        except Exception as err:
            # Логирование ошибок в стандартный логгер
            logging.warning(err)

    def print_tbl(
        self,
        level_style: str,
        level: str,
        file: str,
        line: int,
        message: str = "",
    ) -> str:
        """Форматирует вывод логгера в табличном виде.

        Создает таблицу Rich с колонками для уровня, сообщения и информации о файле.

        Args:
            level_style: Rich разметка для стиля уровня логирования
            level: Название уровня логирования
            file: Имя файла откуда вызван лог
            line: Номер строки в файле
            message: Текст сообщения для вывода

        Returns:
            Захваченный вывод таблицы как строка
        """
        # Создание таблицы Rich без границ и заголовков
        table = Table(
            highlight=True,  # Подсветка синтаксиса
            show_header=False,  # Без заголовков колонок
            padding=0,  # Без отступов
            collapse_padding=True,  # Сжатие отступов
            show_footer=False,  # Без подвала
            expand=True,  # Растягивание на всю ширину
            box=None,  # Без рамки
        )
        # Форматирование метки уровня с выравниванием
        stamp = f"{level_style:<9}"
        # Колонка для уровня логирования (LEVEL)
        table.add_column(
            justify="left",  # Выравнивание по левому краю
            min_width=self.config.LGR_LEVEL_MIN_WITH,  # Минимальная ширина
            max_width=self.config.LGR_LEVEL_MAX_WITH,  # Максимальная ширина
        )
        # Попытка получить пользовательский стиль для уровня
        try:
            style: Any = getattr(self, f"{level}_style")
        except AttributeError:
            # Извлечение стиля из Rich разметки
            match = re.match(r"^\[(.*)].", level_style)
            style = match and match.group(1)
            if style:
                # Удаление reverse из стиля для текста сообщения
                style = style.replace("reverse", "")
        # Колонка для основного сообщения (MESSAGE)
        table.add_column(ratio=self.config.LGR_RATIO_MESSAGE, overflow="fold", style=style)
        # Колонка для информации о файле (FILE)
        table.add_column(justify="right", ratio=self.config.LGR_RATIO_FILE_NAME, overflow="fold")
        # Колонка для отступа справа (LINE)
        table.add_column(ratio=2, overflow="crop")  # для паддинга справа
        # Форматирование содержимого строки таблицы
        msg: str = f"{message}"  # Преобразование сообщения в строку
        file_info: str = f"[grey42]{file}...[/][color(9)]{line}[/]"  # Цветная информация о файле

        # Добавление строки в таблицу
        table.add_row(stamp, msg, file_info)

        # Захват вывода таблицы в строку
        with console.capture() as capture:
            console_dict.print(table, markup=True)
        return capture.get()

    def __getattr__(self, *args: Any, **kwargs: Any) -> Callable[..., None]:
        """Магический метод для создания динамических методов логирования.

        Позволяет вызывать log.любое_слово() для создания логов с соответствующим
        уровнем. Имя метода сохраняется в очереди и используется для поиска стиля.

        Args:
            *args: Первый аргумент - имя вызываемого атрибута
            **kwargs: Дополнительные аргументы (не используются)

        Returns:
            Функция self.print для вызова с аргументами лога
        """
        name: str = args[0]  # Имя вызываемого атрибута

        # Проверка на атрибуты стилей - возвращаем реальный атрибут
        if name.endswith(("style",)):
            return object.__getattribute__(self, name)

        # Сохранение имени уровня в очереди для последующего использования
        self.deque.append(name)
        # Возврат метода print для вызова с аргументами
        return self.print

    def print_message_for_table(self, message: Any) -> str:
        """Форматирует сообщение для вывода в таблице без цветов.

        Создает отдельную консоль Rich без цветового форматирования
        для корректного отображения сложных объектов.

        Args:
            message: Объект для форматирования

        Returns:
            Отформатированная строка без ANSI кодов
        """
        # Создание консоли Rich без цветов и разметки
        console_: Console = Console(
            no_color=True,  # Отключение цветов
            markup=False,  # Отключение Rich разметки
            safe_box=True,  # Безопасные символы для таблиц
            highlight=False,  # Отключение подсветки синтаксиса
        )

        # Захват вывода объекта в строку
        with console_.capture() as capture:
            console_.print(
                message,
                markup=False,  # Без разметки
                width=self.config.LGR_CONSOLE_WITH,  # Ширина из конфигурации
            )
        return capture.get()

    def format_extra_obj(self, message: Any) -> None:
        """Форматирует вывод сложных объектов в цвете и заданной ширине.

        Создает отдельную таблицу для красивого отображения dict, list, tuple
        и других сложных объектов с использованием Rich форматирования.

        Args:
            message: Объект для форматированного вывода (dict, list, tuple и др.)
        """
        # Создание таблицы для сложных объектов
        table = Table(
            padding=(0, 2),  # Отступы слева и справа
            highlight=True,  # Подсветка синтаксиса
            show_footer=False,  # Без подвала
            box=None,  # Без рамки
        )

        # Одна колонка на всю ширину
        table.add_column()

        # Добавление отформатированного объекта в таблицу
        table.add_row(self.print_message_for_table(message=message))

        # Вывод таблицы с разметкой
        console_dict.print(table, markup=True)


# Создание глобального экземпляра логгера с конфигурацией по умолчанию
log = Log(config=get_main_config())
