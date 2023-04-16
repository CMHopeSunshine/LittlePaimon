from typing import Dict

from nonebot import logger as nb_logger
from nonebot.utils import escape_tag


class logger:
    """
    自定义格式、色彩logger
    """

    @staticmethod
    def info(command: str, info: str = '', param: Dict[str, any] = None, result: str = '', result_type: bool = True):
        param_str = ' '.join([f'{k}<m>{escape_tag(str(v))}</m>' for k, v in param.items()]) if param else ''
        result_str = f'<g>{escape_tag(result)}</g>' if result_type else f'<r>{escape_tag(result)}</r>' if result else ''
        nb_logger.opt(colors=True).info(f'<u><y>[{command}]</y></u>{info}{param_str}{result_str}')

    @staticmethod
    def success(command: str, info: str = '', param: Dict[str, any] = None, result: str = ''):
        param_str = ' '.join([f'{k}<m>{escape_tag(str(v))}</m>' for k, v in param.items()]) if param else ''
        result_str = f'<g>{escape_tag(result)}</g>' if result else ''
        nb_logger.opt(colors=True).success(f'<u><y>[{command}]</y></u>{info}{param_str}{result_str}')

    @staticmethod
    def warning(command: str, info: str = '', action: str = ''):
        nb_logger.opt(colors=True).warning(f'<u><y>[{command}]</y></u>{escape_tag(info)}<m>{escape_tag(action)}</m>')

    @staticmethod
    def debug(command: str, info: str):
        nb_logger.opt(colors=True).debug(f'<u><y>[{command}]</y></u>{escape_tag(info)}')
