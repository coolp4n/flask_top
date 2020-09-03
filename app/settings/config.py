# 自定义配置类
class DefaultConfig(object):
    """项目默认配置类  [父类]"""
    # 共同的配置信息
    SCRECT_KEY = "python37"


class DevelopmentConfig(DefaultConfig):
    """开发模式的配置类"""
    DEBUG = True

    # mysql数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:mysql@192.168.243.154:3306/HMTopnews37"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    # redis数据库配置[注意：连接到redis的主数据库]
    REDIS_HOST = "192.168.243.154"
    REDIS_PORT = 6381


class ProductionConfig(DefaultConfig):
    """生产模式的配置类"""
    DEBUG = False


# 暴露字典接口供外键调用
config_dict = {
    "dev": DevelopmentConfig,
    "pro": ProductionConfig
}
