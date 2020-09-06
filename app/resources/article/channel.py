from flask_restful import Resource
from models.article import Channel
from sqlalchemy.orm import load_only


class AllChannelResource(Resource):
    """所有频道信息视图类"""

    def get(self):
        # 1.查询所有的频道信息
        channels = Channel.query.options(load_only(Channel.id, Channel.name)).all()

        # 2.序列化成字典
        channels_dict_list = [channel.to_dict() for channel in channels]

        # 3.返回所有频道信息
        return {"channels": channels_dict_list}
