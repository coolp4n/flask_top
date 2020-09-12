"""随机过期时长"""
import random


class BaseCacheTTL(object):
    # 基础过期时长
    TTL = 60 * 60
    # 随机过期时长最大值
    MAX_DELTA = 60 * 10

    # 类方法
    @classmethod
    def get_val(cls):
        return cls.TTL + random.randint(0, cls.MAX_DELTA)


class UserCacheTTL(BaseCacheTTL):
    """用户过期时间类"""
    # 基础过期时长
    # 用户数据2小时过期基础时长
    TTL = 60 * 60 * 2
    MAX_DELTA = 60 * 20



class UserNotExeistCacheTTL(BaseCacheTTL):
    """用户不存在过期时间类"""
    pass


class AriticleCacheTTL(BaseCacheTTL):
    """文章过期时间类"""
    # 基础过期时长
    # 文章数据2小时过期基础时长
    TTL = 60 * 60 * 2
    MAX_DELTA = 60 * 20
