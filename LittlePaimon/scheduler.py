import logging
from datetime import datetime, date, timedelta
from typing import Optional, Callable, Union
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from nonebot.log import LoguruHandler
from .hook import on_startup, on_shutdown
from .log import logger, Yellow

scheduler = AsyncIOScheduler()
scheduler.configure({'apscheduler.timezone': 'Asia/Shanghai'})


@on_startup()
async def _start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info('定时任务', Yellow('启动定时任务'))


@on_shutdown()
async def _shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info('定时任务', Yellow('关闭定时任务'))


aps_logger = logging.getLogger('apscheduler')
aps_logger.setLevel(30)
aps_logger.handlers.clear()
aps_logger.addHandler(LoguruHandler())


def add_interval_job(
        func: Callable,
        job_id: Optional[str] = None,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        start_date: Union[date, datetime, str] = None,
        end_date: Union[date, datetime, str] = None,
        misfire_grace_time: Optional[int] = None,
        *args,
        **kwargs) -> str:
    """
    使指定函数每隔一段时间执行一次

    :param func: 要执行的函数
    :param job_id: 任务ID，不设置则自动生成
    :param weeks: 周数
    :param days: 天数
    :param hours: 小时
    :param minutes: 分钟
    :param seconds: 秒
    :param start_date: 允许执行的开始日期，不设置则无限制
    :param end_date: 允许执行的结束日期，不设置则无限制
    :param misfire_grace_time: 容错时间
    :param args: 其它传给函数的位置参数
    :param kwargs: 其它传给函数的关键字参数
    :return: 任务ID，可以用于取消任务
    """
    job = scheduler.add_job(func,
                            'interval',
                            weeks=weeks,
                            days=days,
                            hours=hours,
                            minutes=minutes,
                            seconds=seconds,
                            start_date=start_date,
                            end_date=end_date,
                            misfire_grace_time=misfire_grace_time,
                            args=args,
                            kwargs=kwargs,
                            id=job_id)
    return job.id


def on_interval_time(job_id: Optional[str] = None,
                     weeks: int = 0,
                     days: int = 0,
                     hours: int = 0,
                     minutes: int = 0,
                     seconds: int = 0,
                     start_date: Union[date, datetime, str] = None,
                     end_date: Union[date, datetime, str] = None,
                     misfire_grace_time: Optional[int] = None,
                     *args,
                     **kwargs) -> Callable:
    """
    装饰器
    装饰一个函数，使其在指定间隔时间执行

    示例:
    每1分钟执行一次打印test
    ```
    @on_interval_time(minutes=1)
    async def test():
        print('test')
    ```

    :param job_id: 任务ID，不设置则自动生成
    :param weeks: 周数
    :param days: 天数
    :param hours: 小时
    :param minutes: 分钟
    :param seconds: 秒
    :param start_date: 允许执行的开始日期，不设置则无限制
    :param end_date: 允许执行的结束日期，不设置则无限制
    :param misfire_grace_time: 容错时间
    :param args: 其它传给函数的位置参数
    :param kwargs: 其它传给函数的关键字参数
    """

    def inner(func: Callable) -> Callable:
        add_interval_job(func,
                         job_id=job_id,
                         weeks=weeks,
                         days=days,
                         hours=hours,
                         minutes=minutes,
                         seconds=seconds,
                         start_date=start_date,
                         end_date=end_date,
                         misfire_grace_time=misfire_grace_time,
                         args=args,
                         kwargs=kwargs)
        return func

    return inner


def add_cron_job(
        func: Callable,
        job_id: Optional[str] = None,
        crontab: Optional[str] = None,
        year: Union[int, str] = '*',
        month: Union[int, str] = '*',
        week: Union[int, str] = '*',
        day: Union[int, str] = '*',
        day_of_week: Union[int, str] = '*',
        hour: Union[int, str] = '*',
        minute: Union[int, str] = '*',
        second: Union[int, str] = '*',
        start_date: Union[date, datetime, str] = None,
        end_date: Union[date, datetime, str] = None,
        misfire_grace_time: Optional[int] = None,
        *args,
        **kwargs) -> str:
    """
    使指定函数，按cron表达式来定期执行

    :param func: 要执行的函数
    :param job_id: 任务ID，不设置则自动生成
    :param crontab: crontab表达式，如有，则后续year等参数将忽略
    :param year: 年
    :param month: 月
    :param week: 周
    :param day_of_week: 周内第几天或者星期几
    :param day: 天
    :param hour: 小时
    :param minute: 分钟
    :param second: 秒
    :param start_date: 允许执行的开始日期，不设置则无限制
    :param end_date: 允许执行的结束日期，不设置则无限制
    :param misfire_grace_time: 容错时间
    :param args: 其它传给函数的位置参数
    :param kwargs: 其它传给函数的关键字参数
    :return: 任务ID，可用于取消任务
    """
    if crontab:
        job = scheduler.add_job(func,
                                CronTrigger.from_crontab(crontab),
                                misfire_grace_time=misfire_grace_time,
                                args=args,
                                kwargs=kwargs,
                                id=job_id)
    else:
        job = scheduler.add_job(func,
                                'cron',
                                year=year,
                                month=month,
                                day=day,
                                week=week,
                                day_of_week=day_of_week,
                                hour=hour,
                                minute=minute,
                                second=second,
                                start_date=start_date,
                                end_date=end_date,
                                misfire_grace_time=misfire_grace_time,
                                args=args,
                                kwargs=kwargs,
                                id=job_id)
    return job.id


def on_cron_time(
        job_id: Optional[str] = None,
        crontab: Optional[str] = None,
        year: Union[int, str] = '*',
        month: Union[int, str] = '*',
        week: Union[int, str] = '*',
        day: Union[int, str] = '*',
        day_of_week: Union[int, str] = '*',
        hour: Union[int, str] = '*',
        minute: Union[int, str] = '*',
        second: Union[int, str] = '*',
        start_date: Union[date, datetime, str] = None,
        end_date: Union[date, datetime, str] = None,
        misfire_grace_time: Optional[int] = None,
        *args,
        **kwargs):
    """
    装饰器
    装饰一个函数，使其按cron表达式时间执行

    示例:
    在6,7,8,11,12月的第3个周五的1,2,3点打印test
    ```
    @on_cron_time(month='6-8,11-12', day='3rd fri', hour='0-3')
    async def test():
        print('test')
    ```

    :param job_id: 任务ID，不设置则自动生成
    :param crontab: crontab表达式，如有，则后续year等参数将忽略
    :param year: 年
    :param month: 月
    :param week: 周
    :param day_of_week: 周内第几天或者星期几
    :param day: 天
    :param hour: 小时
    :param minute: 分钟
    :param second: 秒
    :param start_date: 允许执行的开始日期，不设置则无限制
    :param end_date: 允许执行的结束日期，不设置则无限制
    :param misfire_grace_time: 容错时间
    :param args: 其它传给函数的位置参数
    :param kwargs: 其它传给函数的关键字参数
    """

    def inner(func: Callable) -> Callable:
        add_cron_job(func,
                     job_id=job_id,
                     crontab=crontab,
                     year=year,
                     month=month,
                     day=day,
                     week=week,
                     day_of_week=day_of_week,
                     hour=hour,
                     minute=minute,
                     second=second,
                     start_date=start_date,
                     end_date=end_date,
                     misfire_grace_time=misfire_grace_time,
                     args=args,
                     kwargs=kwargs)
        return func

    return inner


def add_date_job(
        func: Callable,
        run_date: Union[str, datetime],
        job_id: Optional[str] = None,
        misfire_grace_time: Optional[int] = None,
        *args,
        **kwargs) -> str:
    """
    使一个函数在指定时间执行

    :param func: 要执行的函数
    :param run_date: 执行时间
    :param job_id: 任务ID，不设置则自动生成
    :param misfire_grace_time: 容错时间
    :param args: 其它传给函数的位置参数
    :param kwargs: 其它传给函数的关键字参数
    :return: 任务ID，可用于取消任务
    """
    job = scheduler.add_job(func,
                            'date',
                            run_date=run_date,
                            misfire_grace_time=misfire_grace_time,
                            args=args,
                            kwargs=kwargs,
                            id=job_id)
    return job.id


def on_date_time(
        run_date: Union[str, datetime],
        job_id: Optional[str] = None,
        misfire_grace_time: Optional[int] = None,
        *args,
        **kwargs):
    """
    装饰器
    装饰一个函数，使其在指定时间执行

    :param run_date: 执行时间
    :param job_id: 任务ID，不设置则自动生成
    :param misfire_grace_time: 容错时间
    :param args: 其它传给函数的位置参数
    :param kwargs: 其它传给函数的关键字参数
    """

    def inner(func: Callable) -> Callable:
        add_date_job(func,
                     run_date=run_date,
                     misfire_grace_time=misfire_grace_time,
                     args=args,
                     kwargs=kwargs,
                     job_id=job_id)
        return func

    return inner


def add_run_after_job(seconds: int,
                      func: Callable,
                      *args,
                      **kwargs) -> str:
    """
    使一个函数在指定秒数后执行

    :param seconds: 秒数
    :param func: 函数
    :param args: 其它传给函数的位置参数
    :param kwargs: 其它传给函数的关键字参数
    :return: 任务ID，可用于取消任务
    """
    a = scheduler.add_job(func, 'date', run_date=datetime.now() + timedelta(seconds=seconds), args=args, kwargs=kwargs)
    return a.id


__all__ = [
    'add_interval_job',
    'add_cron_job',
    'add_date_job',
    'add_run_after_job',
    'on_interval_time',
    'on_cron_time',
    'on_date_time',
    'scheduler'
]
