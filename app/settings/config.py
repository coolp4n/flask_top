# 自定义配置类
class DefaultConfig(object):
    """项目默认配置类  [父类]"""
    # 共同的配置信息
    SCRECT_KEY = "python37"
    # restful中不允许ascii编码
    RESTFUL_JSON = {"ensure_ascii": False}

    # 七牛云的配置信息
    QINIU_ACCESS_KEY = 'W0oGRaBkAhrcppAbz6Nc8-q5EcXfL5vLRashY4SI'
    QINIU_SECRET_KEY = 'tsYCBckepW4CqW0uHb9RdfDMXRDOTEpYecJAMItL'
    QINIU_BUCKET_NAME = 'szpython37'
    QINIU_DOMAIN = 'http://qg457zgw6.hn-bkt.clouddn.com/'


class DevelopmentConfig(DefaultConfig):
    """开发模式的配置类"""
    DEBUG = True

    # mysql数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:mysql@192.168.243.154:3306/HMTopnews37"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    SQLALCHEMY_BINDS = {
        "master": 'mysql+pymysql://root:mysql@192.168.243.154:3306/HMTopnews37',  # 主库
        "slave1": 'mysql+pymysql://root:mysql@192.168.243.154:8306/HMTopnews37',  # 从库
        "slave2": 'mysql+pymysql://root:mysql@192.168.243.154:3306/HMTopnews37'  # 从库
    }

    # redis数据库配置[注意：连接到redis的主数据库]
    # TODO: 服务器redis设置外网能够访问
    # REDIS_HOST = "192.168.243.154"
    # REDIS_PORT = 6381
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # JWT 秘钥
    JWT_SECRET = "gVtEg7VAMhKsyMCeeQwIZFfy7TLy7ihurVIRpN2kuxekOJz5tg+yuw=="

    # 用户token过期时长- 2小时过期
    JWT_USER_EXPIRE = 2

    # 刷新token过期时长 - 14天过期
    JWT_REFRESH_EXPIRE = 14


class ProductionConfig(DefaultConfig):
    """生产模式的配置类"""
    DEBUG = False


# 暴露字典接口供外键调用
config_dict = {
    "dev": DevelopmentConfig,
    "pro": ProductionConfig
}
