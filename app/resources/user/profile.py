from flask import g
from flask_restful import Resource
from models.user import User
from utils.decorators import login_required
from sqlalchemy.orm import load_only


# 个人中心类视图
class CurrentUserResource(Resource):
    # 要求必须登录的装饰器
    method_decorators = {"get": [login_required]}

    def get(self):
        # 1.获取当前登录用户user_id
        user_id = g.user_id

        # 2.根据id查询用户信息
        user = User.query.options(load_only(User.id,
                                            User.name,
                                            User.profile_photo,
                                            User.introduction,
                                            User.article_count,
                                            User.following_count,
                                            User.fans_count)).filter(User.id == user_id).first()

        # 3.用户对象序列化成字典
        user_dict = user.to_dict()

        return user_dict
