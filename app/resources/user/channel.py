from flask import g
from flask_restful import Resource
from models.article import Channel, UserChannel
from utils.decorators import login_required
from sqlalchemy.orm import load_only


class UserChannelResource(Resource):
    """当前登录用户的频道信息视图类"""

    """
    思路：
        # 1.获取参数
        # 1.1 当前登录用户 user_id
        # 2.校验参数
        # 3.业务逻辑
        # 3.1 根据用户id查询联合查询频道表和用户频道表，查询到频道id和频道名称
        # 3.1 查询条件：未删除的用户频道，根据序列号排序
        # 3.2 当前用户未选择任何频道，查询默认频道
        # 4.返回值处理
    """
    # method_decorators = {"get": [login_required]}

    def get(self):
        # 1.获取参数
        # 1.1 当前登录用户 user_id
        # 2.校验参数
        user_id = g.user_id
        is_refresh = g.is_refresh
        # 用户已经登录
        if user_id and is_refresh is False:
            # 查询条件：UserChannel.user_id == user_id 用户频道的用户id和当前登录的用户id相同
            # 查询条件：UserChannel.is_deleted == False 未删除的用户频道
            # 排序条件：UserChannel.sequence 用户频道的序号升序
            channels = Channel.query.options(load_only(Channel.id, Channel.name)). \
                join(UserChannel, Channel.id == UserChannel.channel_id). \
                filter(UserChannel.user_id == user_id, UserChannel.is_deleted == False). \
                order_by(UserChannel.sequence).all()

            # 用户已经登录，但是从未收藏任何频道
            if len(channels) == 0:
                # 查询默认频道
                channels = Channel.query.options(load_only(Channel.id, Channel.name)) \
                    .filter(Channel.is_default == True)
        # 用户未登录
        else:
            # 查询默认频道
            channels = Channel.query.options(load_only(Channel.id, Channel.name)) \
                .filter(Channel.is_default == True)

        # 将频道对象列表转换成字典列表
        channel_dict_lit = [channel.to_dict() for channel in channels]

        # 将推荐频道插入到列表的0号下标
        channel_dict_lit.insert(0, {"id": 0, "name": "推荐"})

        # 返回频道列表
        return {"channels": channel_dict_lit}
