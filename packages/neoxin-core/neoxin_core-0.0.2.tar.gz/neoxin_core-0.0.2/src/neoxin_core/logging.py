import logging
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler


# 初始化标志
_initialized = False


def setup_logging(
    log_dir: str | None = None,
    level: str = "INFO",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
):
    """
    初始化日志

    Args:
        log_dir (str | None, optional): 日志目录. Defaults to None.
        level (str, optional): 日志级别. Defaults to "INFO".
    """
    if not log_dir:
        log_dir = "logs"
    global _initialized
    if _initialized:
        return
    logger = logging.getLogger()
    logger.setLevel(level.upper())
    fmt = logging.Formatter(log_format)
    if log_dir:
        p = Path(log_dir)
        p.mkdir(parents=True, exist_ok=True)
        fh = TimedRotatingFileHandler(
            str(p / "app.log"), when="midnight", backupCount=7, encoding="utf-8"
        )
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    _initialized = True


def get_logger(name: str | None = None) -> logging.Logger:
    """
    获取日志

    Args:
        name (str | None, optional): 日志名称. Defaults to None.
    """
    return logging.getLogger(name or "app")
