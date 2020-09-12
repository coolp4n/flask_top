"""
举例：缓存用户对象
redis类型：hash
redis存储命令：hset/hmset key value
redis读取命令：hget/hmget key
redis的key： user:user_id:basic
redis的value： user模型对象 ==> user字典

缓存类: UserCache
属性： user_id
方法： get()  clear()

redis集群充当缓存层
"""
from sqlalchemy.orm import load_only
from .constant import UserCacheTTL, UserNotExeistCacheTTL
from app import redis_cluster
from models.user import User


class UserCache(object):
    """用户基本信息缓存工具类"""

    def __init__(self, user_id):
        # 记录用户id
        self.user_id = user_id
        # redis键
        self.key = "user:{}:basic".format(user_id)

    """
    查询缓存思路：
        # 1.直接查询redis缓存数据
        # 2.缓存存在-返回缓存用户数据
        # 2.1 数据为空字典标志位: {"null": True} ==> 返回空数据
        # 2.2 不是空字典标志位，返回用户字典数据
        # 3.缓存不存在-通过orm机制查询mysql中的用户数据
        # 4.mysql用户存在 - 4.1用户对象转字典，4.2 回填缓存，4.3 并且将数据返回给flask
        # 5.mysql用户不存在 - 防止缓存穿透，将回填一个数据为空的标志位{"null": 1}, 返回空数据给flask
        注意：在回填或者缓存空的标志位都需要设置随机过期时长防止出现-缓存雪崩
    """

    def get(self):
        """
        获取用户缓存
        :return: 用户字典数据 & None
        """
        # 1.直接查询redis缓存数据
        # 如果不存在，返回空字典
        user_data = redis_cluster.hgetall(self.key)

        # 2.缓存存在-返回缓存用户数据
        if user_data:

            # 2.1 数据为空字典标志位: {"null": True} ==> 返回空数据
            if user_data.get("null"):
                return None
            # 2.2 不是空字典标志位，返回用户字典数据
            else:
                return user_data
        else:
            # 3.缓存不存在-通过orm机制查询mysql中的用户数据
            user = User.query.options(load_only(User.id,
                                                User.name,
                                                User.profile_photo,
                                                User.introduction,
                                                User.article_count,
                                                User.fans_count,
                                                User.following_count)). \
                filter(User.id == self.user_id).first()

            # 4.mysql用户存在 - 4.1用户对象转字典，4.2 回填缓存，4.3 并且将数据返回给flask
            if user:
                # 4.1用户对象转字典
                user_dict = user.to_dict()

                print(user_dict)

                # 4.2 回填缓存-用户字典
                redis_cluster.hmset(self.key, user_dict)
                # 设置过期时长-2小时
                # 防止缓存雪崩-设置随机过期时长
                print("过期时长", UserCacheTTL.get_val())
                redis_cluster.expire(self.key, UserCacheTTL.get_val())
                # 4.3 并且将数据返回给flask
                return user_dict

            # 5.mysql用户不存在 - 防止缓存穿透，将回填一个数据为空的标志位{"null": True}, 返回空数据给flask
            else:
                # 回填缓存-为空的字典标志位
                redis_cluster.hmset(self.key, {"null": True})
                redis_cluster.expire(self.key, UserNotExeistCacheTTL.get_val())
                return None

            # TODO：注意：在回填或者缓存空的标志位都需要设置随机过期时长防止出现 - 缓存雪崩

    def clear(self):
        """
        清空缓存: 缓存更新策略 = 先写mysql，防止数据不一致脏数据，再清空缓存,在回填缓存
        """
        # 注意：更新用户数据的时候记得更新mysql数据完成之后调用该方法完成删除缓存
        # 防止出现脏数据
        redis_cluster.delete(self.key)
