import logging
import os
from collections import namedtuple
from collections.abc import Callable
from functools import lru_cache

from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.theme import Theme

__all__ = ["theme", "config_tpl", "config_main", "console", "console_dict"]


@lru_cache
def get_style(
    style: str,
    LOGRICH_DEFAULT_FORMAT: str | None = None,
) -> str:
    """
    Получает стиль форматирования для логов

    Args:
        style (str): Название стиля
        LOGRICH_DEFAULT_FORMAT (Optional[str]): Формат по умолчанию

    Returns:
        str: Строка форматирования
    """
    LOGRICH_DEFAULT_FORMAT = LOGRICH_DEFAULT_FORMAT or os.environ.get(
        "LOGRICH_DEFAULT_FORMAT", "[reverse color(245)] DEF    [/]"
    )
    resp = config_tpl.get(style, LOGRICH_DEFAULT_FORMAT.strip('"'))
    return resp


config_main = namedtuple(
    "config_main",
    # ширина всего вывода
    # ширина вывода имени файла
    (
        "LGR_LOGRICH_ON",  # Условие работы логрича
        "LGR_RATIO_FILE_NAME",  # Доля ширины имени файла в общей ширине
        "LGR_LEVEL_MIN_WITH",  # Наименьшая ширина плашки
        "LGR_LEVEL_MAX_WITH",  # Наибольшая ширина плашки
        "LGR_RATIO_MESSAGE",  # Доля ширины основного сообщения в общей ширине
        "LGR_CONSOLE_WITH",  # Ширина консоли richlog
        "LGR_REDUCE_DEVIDER_LEN",  # На сколько нужно уменьшить разделитель
        "LGR_LEN_FILE_NAME_SECTION",  # Точная ширина контента колонки с именем файла
    ),
)


@lru_cache
def get_main_config() -> config_main:
    """
    Формирует объект с параметрами конфигурации логирования

    Returns:
        config_main: Именованный кортеж с параметрами конфигурации
    """

    def get_env_value(name: str, type_: Callable, default: int | str | bool) -> bool | str | int | None:
        """
        Получает значение из переменных окружения или использует значение по умолчанию

        Args:
            name (str): Название переменной окружения
            type_ (Callable): Тип данных для преобразования
            default (Union[int, str, bool]): Значение по умолчанию

        Returns:
            Union[bool, str, int, None]: Значение переменной или значение по умолчанию
        """
        try:
            val = type_(os.environ.get(name, default=default))
            return val
        except Exception as err:
            logging.warning(
                f"Ошибка в начальных параметрах: {err}\nБудет использовано значение по-умолчанию: {default}."
            )

    try:
        # in docker without tty
        LGR_CONSOLE_WITH = get_env_value("LGR_CONSOLE_WITH", int, os.get_terminal_size()[0])
    except OSError:
        LGR_CONSOLE_WITH = 100

    resp = config_main(
        # условие работы логрича
        LGR_LOGRICH_ON=get_env_value("LGR_LOGRICH_ON", int, True),
        # наибольшая ширина плашки
        LGR_LEVEL_MAX_WITH=get_env_value("LGR_LEVEL_MAX_WITH", int, 15),
        # наименьшая ширина плашки
        LGR_LEVEL_MIN_WITH=get_env_value("LGR_LEVEL_MIN_WITH", int, 9),
        # доля ширины имени файла в общей ширине
        LGR_RATIO_FILE_NAME=get_env_value("LGR_RATIO_FILE_NAME", int, 55),
        # доля ширины основного сообщения в общей ширине
        LGR_RATIO_MESSAGE=get_env_value("LGR_RATIO_MESSAGE", int, 100),
        # насколько нужно уменьшить разделитель - это прерывистая черта отделяющая
        # вывод не помещающийся в одной строке с плашкой
        LGR_REDUCE_DEVIDER_LEN=get_env_value("LGR_REDUCE_DEVIDER_LEN", int, 25),
        # ширина консоли richlog, ее можно установить менее ширины консоли
        LGR_CONSOLE_WITH=LGR_CONSOLE_WITH,
        # точная ширина контента колонки с именем файла
        LGR_LEN_FILE_NAME_SECTION=get_env_value("LGR_LEN_FILE_NAME_SECTION", int, 20),
    )

    return resp


config_tpl: dict[str, str] = dict(
    # https://rich.readthedocs.io/en/stable/appendix/colors.html
    # здесь значения по-умолчанию, для того, чтобы не загромождать
    # файл с переменными окружения
    LOG_LEVEL_ELAPCE_TPL="[reverse turquoise2] ELAPCE [/]",  # Уровень лога:.elapsed
    LOG_LEVEL_START_TPL="[reverse i aquamarine1] START  [/]",  # Уровень лога: start
    LOG_LEVEL_END_TPL="[reverse i green4] END    [/reverse i green4]",  # Уровень лога: end
    LOG_LEVEL_TEST_TPL="[reverse grey70] TEST   [/]",  # Уровень лога: test
    LOG_LEVEL_DATA_TPL="[reverse cornflower_blue] DATA   [/]",  # Уровень лога: data
    LOG_LEVEL_DEV_TPL="[reverse grey70] DEV    [/]",  # Уровень лога: dev
    LOG_LEVEL_INFO_TPL="[reverse blue] INFO   [/]",  # Уровень лога: info
    LOG_LEVEL_TRACE_TPL="[reverse dodger_blue2] TRACE  [/]",  # Уровень лога: trace
    LOG_LEVEL_RUN_TPL="[reverse yellow] RUN    [/]",  # Уровень лога: run
    LOG_LEVEL_GO_TPL="[reverse royal_blue1] GO     [/]",  # Уровень лога: go
    LOG_LEVEL_LIST_TPL="[reverse wheat4] LIST   [/]",  # Уровень лога: list
    LOG_LEVEL_DEBUG_TPL="[reverse #AB343A] DEBUG  [/]",  # Уровень лога: debug
    LOG_LEVEL_SUCCESS_TPL="[reverse green] SUCCS  [/]",  # Уровень лога: success
    LOG_LEVEL_LOG_TPL="[reverse chartreuse4] LOG    [/]",  # Уровень лога: log
    LOG_LEVEL_TIME_TPL="[reverse spring_green4] TIME   [/]",  # Уровень лога: time
    LOG_LEVEL_WARN_TPL="[reverse yellow] WARN   [/]",  # Уровень лога: warn
    LOG_LEVEL_WARNING_TPL="[reverse yellow] WARN   [/]",  # Уровень лога: warning
    LOG_LEVEL_FATAL_TPL="[reverse bright_red] FATAL  [/]",  # Уровень лога: fatal
    LOG_LEVEL_ERR_TPL="[reverse #ff5252] ERR    [/]",  # Уровень лога: err
    LOG_LEVEL_ERROR_TPL="[reverse #ff5252] ERROR  [/]",  # Уровень лога: error
)

config_tpl.update(
    **os.environ,  # override loaded values with environment variables
)

color_of_digit = "bold magenta"

theme: Theme = Theme(
    # https://www.w3schools.com/colors/colors_picker.asp
    # https://htmlcolorcodes.com/color-names/
    # https://colorscheme.ru/
    {
        "repr.brace": "bold black",  # Фигурные скобки в repr
        "repr.str": "green",  # Строки в repr
        "repr.attrib_name": "#0099ff",  # Имена атрибутов в repr
        "repr.equal": "red dim",  # Знак равенства в repr
        "repr.digit": color_of_digit,  # Цифры в repr
        "repr.digit2": color_of_digit,  # Цифры в repr (второй стиль)
        "repr.colon": "#D2691E",  # Двоеточия в repr
        "repr.quotes": "#778899",  # Кавычки в repr
        "repr.comma": "#778899",  # Запятые в repr
        "repr.key": "#08e8de",  # Ключи в repr
        "repr.bool_true": "bold blue",  # Логические значения True в repr
        "repr.none": "blue",  # None в repr
        "repr.bool_false": "yellow",  # Логические значения False в repr
        "repr.class_name": "magenta bold",  # Имена классов в repr
        "repr.string_list_tuple": "green",  # Строки в списках/кортежах
        "trace_msg": "#05a7f7",  # Сообщения трассировки
        "debug_msg": "#e64d00",  # Сообщения отладки
        "info_msg": "#33ccff",  # Информационные сообщения
        "success_msg": "green",  # Сообщения об успехе
        "warning_msg": "yellow",  # Предупреждения
        "error_msg": "#ff5050",  # Ошибки
        "critical_msg": "#de0b2e",  # Критические ошибки
    },
)


def combine_regex(*regexes: str) -> str:
    """
    Объединяет несколько регулярных выражений в одно

    Args:
        *regexes (str): Регулярные выражения для объединения

    Returns:
        str: Новое регулярное выражение с объединенными 패ternами
    """
    return "|".join(regexes)


class MyReprHighlighter(ReprHighlighter):
    """
    Подсветка вывода на основе регулярных выражений

    Этот класс наследуется от ReprHighlighter и определяет правила подсветки
    различных элементов при выводе repr() объектов.
    """

    # https://regex101.com/r/zR2hP5/1
    base_style = "repr."
    highlights = [
        r"'(?P<str>[\S\s]*)'",
        r":\s\'(?P<value>.+)\'",
        r"['](?P<string_list_tuple>\w+)[']",
        r"(?P<digit2>\d*)[\"\s,[,(](?P<digit>\d*\.?\s?-?\d*-?\.?\d+)",
        combine_regex(
            r"(?P<brace>[][{}()])",  # noqa
            r"\'(?P<key>[\w-]+)\'(?P<colon>:)",
            r"(?P<comma>,)\s",
        ),
        r"(?P<quotes>\')",
        r"(?P<equal>=)",  # noqa
        r"(?P<class_name>[A-Z].*)\(",
        r'(?P<attrib_name>[\w_]{1,50})=(?P<attrib_value>"?[\w_]+"?)?',
        r"\b(?P<bool_true>True)\b|\b(?P<bool_false>False)\b|\b(?P<none>None)\b",
    ]


console: Console = Console()

# инстанс консоли rich
console_dict: Console = Console(
    highlighter=MyReprHighlighter(),
    theme=theme,
    markup=True,
    log_time=False,
    log_path=False,
    safe_box=True,
)
