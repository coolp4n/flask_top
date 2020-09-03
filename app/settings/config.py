# 自定义配置类
class DefaultConfig(object):
    """项目默认配置类  [父类]"""
    # 共同的配置信息
    SCRECT_KEY = "python37"


class DevelopmentConfig(DefaultConfig):
    """开发模式的配置类"""
    DEBUG = True

    # TODO: mysql数据库配置
    # TODO: redis数据库配置


class ProductionConfig(DefaultConfig):
    """生产模式的配置类"""
    DEBUG = False


# 暴露字典接口供外键调用
config_dict = {
    "dev": DevelopmentConfig,
    "pro": ProductionConfig
}
