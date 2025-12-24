import threading

def singleton(cls):
    """
    装饰器：将类转换为单例模式[线程安全]。
    
    :param cls: 要转换为单例的类
    :return: 单例类的实例获取函数
    """
    instances = {}
    lock = threading.Lock()
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance