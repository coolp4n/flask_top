from flask import g
from flask_restful import Resource
from sqlalchemy.orm import load_only
from datetime import datetime

from app import db
from models.user import Relation, User
from utils.decorators import login_required
from flask_restful.reqparse import RequestParser


class UserFollowingResource(Resource):
    """用户关注接口[POST]& 获取用户关注列表接口[GET] 类视图"""

    method_decorators = {"post": [login_required], 'get': [login_required]}

    """
        思路：
            # 1.获取参数
            # 1.1 当前登录的用户id： user_id
            # 2.参数校验
            # 3.逻辑处理
            # 3.1 根据当前登录的用户id去查询用户表关注作者信息列表：作者名称，作者头像，作者粉丝数量
            # 3.2 获取当前用户的粉丝列表
            # 3.3 判断当前用户的关注列表和粉丝列表id值是否一致,相互关注
            # 4.返回值处理
            
            举例：当前用户user_id  = curry
            关注列表：[kobe, james]
            kobe.id = 1
            粉丝列表：[kobe, harden]
            kobe.id = 1
            curry和kobe是相互关注的关系
        """

    def get(self):
        """获取当前登录用户的关注列表"""
        # 1.获取参数
        # 1.1 当前登录的用户id： user_id
        # 1.2 当前页码，每一页多少条数据
        # 2.参数校验
        # 当前登录用户：curry
        user_id = g.user_id

        parser = RequestParser()
        # 当前页 默认值：1
        parser.add_argument("page", default=1, location="args", type=int)
        # 每一页数量 默认值：10
        parser.add_argument("per_page", default=10, location="args", type=int)
        ret = parser.parse_args()
        page = ret.page
        per_page = ret.per_page

        # 3.逻辑处理
        # 3.1 根据当前登录的用户id去查询用户表关注作者信息列表：作者名称，作者头像，作者粉丝数量
        # join条件：User.id == Relation.author_id 用户id和作者id相等
        # 查询条件：Relation.user_id == user_id 当前用户id和粉丝id相等
        # 查询条件：Relation.relation == Relation.RELATION.FOLLOW 已经关注
        # 排序条件：order_by(Relation.update_time.desc()) 按照关注时间降序排序
        # 分页：paginate(page, per_page)
        paginate_obj = User.query.options(load_only(User.id,
                                                    User.name,
                                                    User.profile_photo,
                                                    User.fans_count)) \
            .join(Relation, User.id == Relation.author_id) \
            .filter(Relation.user_id == user_id,
                    Relation.relation == Relation.RELATION.FOLLOW).\
            order_by(Relation.update_time.desc()).paginate(page,per_page)

        # 当前用户的关注列表
        following_list = paginate_obj.items
        # 当前总页数
        total_page = paginate_obj.pages
        # 当前页
        current_page = paginate_obj.page

        # 3.2 获取当前用户的粉丝列表
        # Relation.user_id 查询粉丝id
        fans_list = Relation.query.options(load_only(Relation.user_id)) \
            .filter(Relation.author_id == user_id).all()
        # 3.3遍历关注列表，将对象转换成字典，同时  判断当前用户的关注列表和粉丝列表id值是否一致,相互关注
        followings = []
        for item in following_list:
            following_dict = {
                "id": item.id,
                "name": item.name,
                "photo": item.profile_photo,
                "fans_count": item.fans_count,
                "mutual_follow": False  # 未关注
            }
            # 判断当前用户的关注列表和粉丝列表id值是否一致,相互关注
            """
            举例：当前用户user_id  = curry  = 3 
            关注列表：[kobe, james]
            kobe.id = 1
            粉丝列表：[kobe, harden]
            kobe.user_id = 1
            curry和kobe是相互关注的关系
            """
            for fans in fans_list:
                # 粉丝id == 作者id
                # kobe.user_id = 1
                # kobe.id = 1
                if fans.user_id == item.id:
                    # 相互关注
                    following_dict["mutual_follow"] = True
                    break

            # 关注字典添加到列表中
            followings.append(following_dict)

        return {
            "results": followings,
            "total_count": total_page,
            "page": page,
            "per_page": per_page
        }

    """
    思路：
        # 1.获取参数
        # 1.1 当前登录的用户id： user_id
        # 1.2 关注的作者id：author_id
        # 2.参数校验
        # 3.逻辑处理
        # 3.1 根据user_id和author_id查询用户关系模型
        # 3.2 用户关系对象存在：将关系修改为：关注，更新关注时间
        # 3.3 用户关系对象不存在：新建关系模型对象，添加到数据
        # 3.4 当前登录用户关注数量加一
        # 3.5 让作者的粉丝数量加一
        # 注意：上述修改提交到数据库
        # 4.返回值处理
    
    """

    def post(self):
        # 1.获取参数
        # 1.1 当前登录的用户id： user_id
        # 1.2 关注的作者id：author_id
        # 2.参数校验
        # 粉丝id：张三
        user_id = g.user_id

        # 作者id: 李四
        parser = RequestParser()
        parser.add_argument("target", required=True, location="json", type=int)
        ret = parser.parse_args()
        author_id = ret.target

        # 3.逻辑处理
        # 3.1 根据user_id和author_id查询用户关系模型
        relation_obj = Relation.query.options(load_only(Relation.id)) \
            .filter(Relation.user_id == user_id, Relation.author_id == author_id).first()  # type:Relation

        # 3.2 用户关系对象存在：将关系修改为：关注，更新关注时间
        if relation_obj:
            # 关注成功
            relation_obj.relation = Relation.RELATION.FOLLOW
            # 修改关注时间
            relation_obj.update_time = datetime.now()

        # 3.3 用户关系对象不存在：新建关系模型对象，添加到数据
        else:
            # 新建关注关系模型对象
            relation_obj = Relation(user_id=user_id, author_id=author_id, relation=Relation.RELATION.FOLLOW)
            db.session.add(relation_obj)

        # 3.4 当前登录用户关注数量加一
        User.query.filter(User.id == user_id).update({"following_count": User.following_count + 1})

        # 3.5 让作者的粉丝数量加一
        User.query.filter(User.id == author_id).update({"fans_count": User.fans_count + 1})

        # TODO: 记得将上述修改提交到数据库
        db.session.commit()

        # 4.返回值处理
        return {"target": author_id, "message": "关注作者成功"}
