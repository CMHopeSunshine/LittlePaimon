import sys
from typing import Union, TYPE_CHECKING

from loguru import logger as loguru_logger
from nonebot.log import logger_id, logger as nb_logger
from rich.console import Console

if TYPE_CHECKING:
    from loguru import Record


def log_format(record: "Record") -> str:
    # if record['message'] == 'NoneBot is initializing...':
    #     record['message'] = '正在初始化Nonebot...'
    return ("<g>{time:MM-DD HH:mm:ss:SSS}</g> "
            "[<lvl>{level}</lvl>] "
            "<c><u>{name}</u></c> | "
            "{message}\n")


def log_filter(record: "Record") -> bool:
    """默认的日志过滤器，根据 `config.log_level` 配置改变日志等级。"""
    # if record['message']:
    #     return False
    log_level = record['extra'].get('nonebot_log_level', 'INFO')
    level_no = nb_logger.level(log_level).no if isinstance(log_level, str) else log_level
    return record['level'].no >= level_no


def init_logger():
    nb_logger.remove(logger_id)
    nb_logger.add(
        sys.stdout,
        level=0,
        format=log_format,
        filter=log_filter,
        backtrace=False,
        diagnose=True,
    )


class logger:
    """
    自定义格式、色彩logger
    """
    _logger: loguru_logger = nb_logger
    _new_level = _logger.level('data', no=38, color='<yellow>', icon='📂')
    _rich_console = Console()

    @classmethod
    def info(cls, command: str, info: str = '', **kwargs):
        """
        info日志

        :param command: 命令名
        :param info: 信息
        """
        cls._logger.opt(colors=True, **kwargs).info(f'{CommandColor(command)}{info}')

    @classmethod
    def success(cls, command: str, info: str = '', **kwargs):
        """
        success日志

        :param command: 命令名
        :param info: 信息
        """
        cls._logger.opt(colors=True, **kwargs).success(f'{CommandColor(command)}{info}')

    @classmethod
    def warning(cls, command: str, info: str = '', **kwargs):
        """
        warning日志

        :param command: 命令名
        :param info: 信息
        """
        cls._logger.opt(colors=True, **kwargs).warning(f'{CommandColor(command)}{info}')

    @classmethod
    def debug(cls, command: str, info: str = '', **kwargs):
        """
        debug日志

        :param command: 命令名
        :param info: 信息
        """
        cls._logger.opt(colors=True, **kwargs).debug(f'{CommandColor(command)}{info}')

    @classmethod
    def error(cls, command: str, info: str = '', **kwargs):
        """
        error日志

        :param command: 命令名
        :param info: 信息
        """
        cls._logger.opt(colors=True, **kwargs).error(f'{CommandColor(command)}{info}')

    @classmethod
    def data(cls, command: str, info: str = '', **kwargs):
        """
        data日志

        :param command: 命令名
        :param info: 信息
        """
        cls._logger.opt(colors=True, **kwargs).log('data', f'{CommandColor(command)}{info}')

    @classmethod
    def exception(cls, command: str, info: str = '', rich: bool = False, **kwargs):
        """
        exception日志

        :param command: 命令名
        :param info: 信息
        :param rich: 使用rich库打印异常
        """
        if rich:
            cls._logger.opt(colors=True, **kwargs).error(f'{CommandColor(command)}{info}')
            cls._rich_console.print_exception(show_locals=True)
        else:
            cls._logger.opt(colors=True, **kwargs).exception(f'{CommandColor(command)}{info}')

    @classmethod
    def status(cls, command: str, message: str, color: str = 'green'):
        """
        状态动画

        :param command: 命令名
        :param message: 消息
        :param color: 颜色
        :return:
        """
        return cls._rich_console.status(
            f'[bold underline yellow][{command}][/bold underline yellow][{color}]{message}[/{color}]',
            spinner='earth')


# def ParamColor(**kwargs) -> str:
#     """参数颜色"""
#     text = ''.join(f'{key}=<m>{value}</m> ' for key, value in kwargs.items())
#     return text.strip()


def CommandColor(command: Union[str, int]):
    """命令颜色"""
    return f'<u><y>[{command}]</y></u>'


def Underline(text: Union[str, int]) -> str:
    """下划线"""
    return f'<u>{text}</u>'


def Yellow(text: Union[str, int]) -> str:
    """黄色"""
    return f'<y>{text}</y>'


def Green(text: Union[str, int]) -> str:
    """绿色"""
    return f'<g>{text}</g>'


def Red(text: Union[str, int]) -> str:
    """红色"""
    return f'<r>{text}</r>'


def Magenta(text: Union[str, int]) -> str:
    """品红色"""
    return f'<m>{text}</m>'


def Bold(text: Union[str, int]) -> str:
    """粗体"""
    return f'<b>{text}</b>'


__all__ = [
    'logger',
    # 'ParamColor',
    'CommandColor',
    'Underline',
    'Yellow',
    'Green',
    'Red',
    'Magenta',
    'Bold',
    'init_logger'
]
