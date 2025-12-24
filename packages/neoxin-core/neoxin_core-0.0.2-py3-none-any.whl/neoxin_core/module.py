import inspect
from .db import Base, get_engine,execute_sql_files
from .logging import get_logger


logger = get_logger('neocore.module')

def init_common_models(
    models: list[type[Base]],
    init_sql_files: list[str] | str | None = None,
    load_sql_files: list[str] | str | None = None,
):
    """
    初始化数据库模型。
    该函数会根据定义的模型类创建数据库表。
    如果表不存在，则会创建表。
    如果表已存在，则不会重复创建。

    Args:
        models (list[type[Base]]): 数据库模型类列表。
        init_sql_files (list[str] | str | None, optional): 初始化SQL文件路径列表或单个路径。默认值为None。
        load_sql_files (list[str] | str | None, optional): 加载SQL文件路径列表或单个路径。默认值为None。
    """
    engine = get_engine()

    inspector = inspect(engine) # type: ignore
    # 检查哪些模型类的表不存在
    missing: list[str] = []
    for m in models:
        if not inspector.has_table(m.__tablename__):
            logger.info(f"表 {m.__tablename__} 不存在，创建表")
            m.__table__.create(bind=engine, checkfirst=True)
            missing.append(m.__tablename__)

    if missing and init_sql_files:
        logger.info(f"初始化SQL文件 {init_sql_files} 会在创建表 {missing} 后执行")
        # 初始化SQL文件会在创建表后执行
        execute_sql_files(init_sql_files or [])
    if load_sql_files:
        logger.info(f"加载SQL文件 {load_sql_files} 会在初始化SQL文件执行后执行")
        # 加载SQL文件会在初始化SQL文件执行后执行
        execute_sql_files(load_sql_files or [])



class ModuleManager:
    def __init__(self):
        self.modules = []