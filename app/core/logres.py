import os
import sys
from datetime import datetime

from loguru import logger
import logging
from .config import settings


class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


def init_logger():
    now = datetime.now()

    rotation = "1 hour"
    retention = "3 days"
    encoding = "utf-8"
    backtrace = True
    diagnose = True
    enqueue = True
    folder = "./logs/" + now.strftime("%Y-%m-%d") + "/"

    # 格式里面添加了process和thread记录，方便查看多进程和线程程序
    format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> "
        "| <magenta>{process}</magenta>:<yellow>{thread}</yellow> "
        "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<yellow>{line}</yellow> - <level>{message}</level>"
    )

    # 生成基于当前日期的日志文件名
    date_str = now.strftime("%Y-%m-%d_%H")
    debug_log_path = folder + f"debug_{date_str}.log"
    error_log_path = folder + f"error_{date_str}.log"

    logger_name_list = [name for name in logging.root.manager.loggerDict]
    logging.root.manager.loggerDict.clear()
    for logger_name in logger_name_list:
        logging.getLogger(logger_name).setLevel(10)
        logging.getLogger(logger_name).handlers = []
        if "." not in logger_name:
            logging.getLogger(logger_name).addHandler(InterceptHandler())

    logger.remove()

    if settings.DEBUG_LOG:
        logger.add(
            debug_log_path,
            level="DEBUG",
            enqueue=enqueue,
            rotation=rotation,
            retention=retention,
            format=format,
            encoding=encoding,
            filter=lambda record: record["level"].no >= logger.level("DEBUG").no,
        )

    if settings.ERROR_LOG:
        logger.add(
            error_log_path,
            level="ERROR",
            enqueue=enqueue,
            backtrace=backtrace,
            diagnose=diagnose,
            rotation=rotation,
            retention=retention,
            format=format,
            encoding=encoding,
            delay=True,
            filter=lambda record: record["level"].no >= logger.level("ERROR").no,
        )

    if settings.STDERR_LOG:
        logger.add(
            sys.stderr,
            level=f"{settings.LOG_LEVEL}",
            format=format,
            colorize=True,
            filter=lambda record: record["level"].no >= logger.level(f"{settings.LOG_LEVEL}").no,
        )
