from sqlalchemy.orm import load_only
from .constant import UserCacheTTL, UserNotExeistCacheTTL, UserFollowingCacheTTL
from app import redis_cluster
from models.user import User, Relation

"""
=============================
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

============用户关注列表【zset集合缓存】===============
举例：用户关注列表缓存
redis类型：zset
redis存储命令： zadd key score value  [API参数顺序不一样， 不同的redis版本这个函数的参数也不一样]
redis中zadd函数，在redis3.0之后的版本传入的数据是字典: {value: score}
redis中zadd函数，在redis2.0的版本传入的数据是字典: (value, score)
redis中读取命令：zrange key 0 -1 [升序]    zrevrange key  0 -1 [降序]
redis的key： user:user_id:followings
redis的value： 列表 [author_id, .....] or []

缓存类： UserFollowingCache
属性：  user_id  key
方法：  get()  update()
"""


class BaseUserFollowCache(object):
    """用户关注、分类列表类的基类"""

    def __init__(self):
        # redis的键
        self.key = ""
        self.count_key = ""
        self.user_id = ""

    def get(self, page, per_page):
        """
        获取当前登录的用户的关注列表[分页]

        # page 当前页码
        # per_page 每一页多少条数据
        :return:作者id列表或者是空列表 [author_id，....]  or []
        """
        # 1.判断数据库是否存在缓存
        is_key_exists = redis_cluster.exists(self.key)

        # 起始下标 = (页码 - 1) * 每页条数
        start_index = (page - 1) * per_page
        # 结束下标 = 起始下标 + 每页条数 - 1
        end_index = start_index + per_page - 1

        if is_key_exists:
            # 2.如果存在缓存，读取缓存数据 zrevrange [时间降序排序 + 分页]
            # 返回值：[author_id, ...] or []
            return redis_cluster.zrevrange(self.key, start_index, end_index)
        else:
            # 3.如果不存在缓存, 查询当前用户的缓存数据
            user_dict = UserCache(user_id=self.user_id).get()

            # 4.判断用户是否存在，同时用户的关注数量follow_count是否为0
            # 4.判断用户是否存在，同时用户的粉丝数量fans_count是否为0
            if user_dict and user_dict[self.count_key]:
                # 查询关注列表或者粉丝列表
                followings = self.db_query()

                # 根据关注还是粉丝列表取出属性名称
                # follow_count 关注列表 ==> 作者对象 ==> getattr(作者对象, "author_id")
                # fans_count   粉丝列表 ==> 粉丝对象 ==> getattr(粉丝对象, "user_id")
                property_name = "author_id" if self.count_key == "follow_count" else "user_id"

                # 5.1 将关系对象回填到redis缓存，设置随机过期时长
                author_fans_list = []
                for item in followings:
                    # item = 作者对象 or 粉丝对象
                    # id  = item.author_id  or item.user_id
                    # TODO ：存储作者id或者粉丝id
                    # 往有序集合中添加数据
                    # score  更新时间
                    # value  作者id或者粉丝id
                    # redis_cluster.zadd(self.key, score , value)
                    id = getattr(item, property_name)
                    # 缓存回填
                    redis_cluster.zadd(self.key, item.update_time.timestamp(), id)

                    # 5.2 将查询到的关注的作者id & 粉丝id添加到列表，分页返回
                    author_fans_list.append(id)

                # 设置随机过期时长-防止出现缓存雪崩
                redis_cluster.expire(self.key, UserFollowingCacheTTL.get_val())

                # 分页返回
                if len(author_fans_list) >= start_index + 1:
                    try:
                        # 第二页： end_index = 10 + 10 - 1 = 19
                        # 假设只有一共13条数据，end_index实际值：12，那么使用end_index=19就会报错
                        # end_index+1 开区间
                        return author_fans_list[start_index: end_index + 1]
                    except Exception as e:
                        # author_id_list[10: 13]
                        return author_fans_list[start_index:]
                else:
                    # 数组越界了
                    return []

            else:
                # 6 如果关注数量为0，返回空的关注列表
                return []

    def update(self, author_id, is_follow, updatetime=0):
        """
        :param author_id:  关注或者取消关注的作者id
        :param is_follow:  标记关注还是取消关注
        :param updatetime: 关注或者取消关注的时间戳
        :return:

         更新关注列表缓存数据
         # 更新关注
         # 更新取消关注
         目的：防止mysql和redis数据不一致的问题出现

        """

        # 1.先查询缓存中是否存在关注列表数据-不需要更新
        is_key_exists = redis_cluster.exists(self.key)
        if not is_key_exists:
            return

        if is_follow:
            # 2.关注
            redis_cluster.zadd(self.key, updatetime, author_id)
        else:
            # 3.取消关注
            redis_cluster.zrem(self.key, author_id)


class UserFollowingCache(BaseUserFollowCache):
    """用户关注列表缓存类"""

    def __init__(self, user_id):
        # 保存用户id
        self.user_id = user_id
        # redis的键
        self.key = "user:{}:followings".format(self.user_id)

        # 获取关注数量
        self.count_key = "follow_count"

    """
    获取当前用户关注列表缓存思路：
        # 1.判断数据库是否存在缓存
        # 2.如果存在缓存，读取缓存数据 zrevrange [时间降序排序 + 分页]
        # 3.如果不存在缓存, 再查询mysql数据库
        # 4.判断用户是否存在，同时用户的关注数量follow_count是否为0 
        # 5 如果关注数量不为0，再查询mysql数据库
        # 5.1 将关系对象回填到redis缓存，设置随机过期时长
        # 5.2 将查询到的关注的作者id添加到列表，分页返回
        # 6 如果关注数量为0，返回空的关注列表
    """

    def db_query(self):
        # 5 如果关注数量不为0，再查询mysql数据库
        return Relation.query.options(load_only(Relation.author_id,
                                                Relation.update_time)) \
            .filter(Relation.user_id == self.user_id,
                    Relation.relation == Relation.RELATION.FOLLOW) \
            .order_by(Relation.update_time.desc()).all()


class UserFansCache(BaseUserFollowCache):
    """用户粉丝列表缓存类"""

    def __init__(self, user_id):
        # 保存用户id
        self.user_id = user_id
        # redis的键
        self.key = "user:{}:fans".format(self.user_id)
        # 获取粉丝数量
        self.count_key = "fans_count"

    def db_query(self):
        # 如果粉丝数量不为0，再查询mysql数据库，粉丝列表
        # 查询Relation.user_id粉丝id
        return Relation.query.options(load_only(Relation.user_id,
                                                Relation.update_time)) \
            .filter(Relation.author_id == self.user_id,
                    Relation.relation == Relation.RELATION.FOLLOW) \
            .order_by(Relation.update_time.desc()).all()

    def has_fans(self, author_id):
        """
        需求：查询作者是否在当前用户的粉丝列表中
        已经有了一个前提：当前用户关注了作者

        当前用户：curry
        关注列表：[kobe, james]
        粉丝列表：[kobe, harden]

        如果在：  当前作者关注了当前用户  ==> 相互关注'
        如果不在：当前作者未关注了当前用户 ==> 未相互关注
        :param author_id: 作者id
        :return: True 相互关注  False 未相互关注
        """
        # 缓存中粉丝列表是否存在
        is_key_exists = redis_cluster.exists(self.key)

        if not is_key_exists:
            # 缓存中粉丝列表不存在
            # 1.缓存过期--手动触发查询myqsl，回填缓存
            items = self.get(1, 1)
            # 2.没有粉丝
            if len(items) == 0:
                # 未相互关注
                return False

        # 有缓存：粉丝列表，查询当前作者是否在粉丝列表中，如果在：当前作者关注了当前用户  前提：当前用户关注了作者
        # 返回True 相互关注
        # zscore 时间复杂度O(1)
        # 如果根据作者id能从粉丝列表中查出分数 => 查询当前作者在粉丝列表中 =>当前作者关注了当前用户 => True
        score = redis_cluster.zscore(self.key, author_id)

        # 细节：如果根据作者id能从粉丝列表中查出分数为0代表作者不是用户的粉丝 => False
        return True if score else False




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
                if not redis_cluster.exists(self.key):
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
