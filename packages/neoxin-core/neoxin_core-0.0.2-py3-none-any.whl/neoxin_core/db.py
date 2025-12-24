"""
数据库模块

提供数据库连接和会话管理功能。
"""

from functools import lru_cache
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import Column, Integer, DateTime
from .logging import get_logger
from .settings import get_settings

logger = get_logger("DB")


class Base(DeclarativeBase):
    """
    数据库模型基类。
    所有数据库模型类都应继承自该类。
    """

    id = Column(Integer, primary_key=True, comment="主键ID")

    # 创建时间
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False, comment="创建时间"
    )

    # 更新时间
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="更新时间",
    )

    def to_dict(self):
        """将模型转换为字典

        Returns:
            dict: 模型字典表示
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    def __repr__(self):
        """模型的字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>"


@lru_cache(maxsize=10)
def get_engine():
    """
    获取数据库引擎。
    该函数会返回一个数据库引擎，用于连接数据库。
    """
    # Import here to avoid circular dependency

    settings = get_settings()
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
        echo=settings.debug,
        future=True,
    )


@lru_cache(maxsize=1)
def get_session_local():
    """
    获取数据库会话本地工厂。
    该函数会返回一个会话本地工厂，用于创建数据库会话。
    """
    return sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)


def create_tables():
    """
    创建数据库表。
    该函数会根据定义的模型类创建数据库表。
    """
    logger.info("创建所有数据库表")
    Base.metadata.create_all(bind=get_engine(), checkfirst=True)


def drop_tables():
    """
    删除数据库表。
    该函数会删除所有数据库表。
    """
    logger.info("删除所有数据库表")
    Base.metadata.drop_all(bind=get_engine())


def execute_sql_files(paths: list[str] | str):
    """
    执行SQL脚本文件。
    该函数会执行指定路径的SQL脚本文件。
    每个脚本文件中的SQL语句会被分号分隔，每个语句会被单独执行。

    Args:
        paths (list[str] | str): SQL脚本文件路径列表或单个路径。
    """
    engine = get_engine()
    files: list[str]
    if isinstance(paths, str):
        files = [paths]
    else:
        files = list(paths or [])
    if not files:
        logger.warning("未指定SQL脚本文件路径")
        return
    with engine.begin() as conn:
        for fp in files:
            try:
                logger.info(f"执行SQL脚本文件 {fp}")
                with open(fp, "r", encoding="utf-8") as f:
                    sql = f.read()
            except Exception:
                logger.error(f"执行SQL脚本文件 {fp} 失败", exc_info=True)
                continue
            statements = [s.strip() for s in sql.split(";") if s.strip()]
            logger.info(f"SQL脚本文件 {fp} 包含 {len(statements)} 条语句")
            for stmt in statements:
                try:
                    conn.exec_driver_sql(stmt)
                    logger.info(f"执行SQL语句 {stmt} 成功")
                except Exception:
                    logger.error(f"执行SQL语句 {stmt} 失败", exc_info=True)

