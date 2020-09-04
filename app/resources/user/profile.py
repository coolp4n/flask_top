from flask import g, request
from flask_restful import Resource, marshal_with, marshal

from app import db
from models.user import User
from utils.decorators import login_required
from sqlalchemy.orm import load_only
from flask_restful.reqparse import RequestParser
from utils.parser import imgtype
from utils.img_storage import upload_file


class UserPhotoResource(Resource):
    """修改头像类视图"""

    # 局部刷新数据: patch
    # put post get del
    """
    思路：
    # 1.获取参数
    # 1.1 photo前端上传的图片数据
    # 1.2 user_id 从g对象中获取
    # 2.校验参数
    # 3.逻辑处理
    # 3.1 提取图片二进制数据，使用封装的图片上传工具类将图片保存到七牛云
    # 3.2 图片的url地址，将用户对象中用户头像url进行更新，提交到数据库
    # 4.返回值处理
    # 4.1 将完整的图片url地址返回给前端
    """
    method_decorators = {"patch": [login_required]}

    def patch(self):

        # 1.获取参数
        # 1.1 photo前端上传的图片数据
        # 1.2 user_id 从g对象中获取
        # 2.校验参数
        parser = RequestParser()
        # request.args
        # request.form
        # request.json
        # request.files
        parser.add_argument("photo",
                            required=True,
                            location='files',
                            type=imgtype)

        # 开始解析
        ret = parser.parse_args()
        photo_file = ret.photo

        # 获取user_id
        user_id = g.user_id

        # 3.逻辑处理
        # 3.1 提取图片二进制数据，使用封装的图片上传工具类将图片保存到七牛云
        photo_bytes = photo_file.read()
        # photo_file.save() 保存到本地
        try:
            imgName, full_url = upload_file(photo_bytes)
        except Exception as e:
            return {"message": "Third Error: {}".format(e)}, 500

        # 3.2 图片的url地址，将用户对象中用户头像url进行更新，提交到数据库
        # 问题：保存图片名称 还是 保存图片完整url地址？？？
        # 最好的保存图片的名称
        User.query.filter(User.id == user_id).update({"profile_photo": full_url})

        # 提交修改头像操作
        db.session.commit()

        # 4.返回值处理
        # 4.1 将完整的图片url地址返回给前端
        return {"full_url": full_url}


# 个人中心类视图
class CurrentUserResource(Resource):
    # 要求必须登录的装饰器
    method_decorators = {"get": [login_required]}

    def get(self):
        # 1.获取当前登录用户user_id
        user_id = g.user_id

        # 2.根据id查询用户信息
        # select * from xxtable where id = user_id
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
