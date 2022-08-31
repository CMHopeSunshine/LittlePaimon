import datetime
from LittlePaimon.utils import scheduler, logger
from LittlePaimon.database.models import GuessVoiceRank, PluginStatistics, DailyNoteSub, CookieCache, PublicCookie


@scheduler.scheduled_job('cron', hour=0, minute=0, misfire_grace_time=10)
async def _():
    now = datetime.datetime.now()

    logger.info('原神实时便签', '重置每日提醒次数限制')
    await DailyNoteSub.all().update(today_remind_num=0)

    logger.info('原神Cookie', '清空每日Cookie缓存和限制')
    await CookieCache.all().delete()
    await PublicCookie.filter(status=2).update(status=1)

    logger.info('功能调用统计', '清除超过一个月的统计数据')
    await PluginStatistics.filter(time__lt=now - datetime.timedelta(days=30)).delete()

    if now.weekday() == 0:
        logger.info('原神猜语音', '清空每周排行榜')
        await GuessVoiceRank.all().delete()
