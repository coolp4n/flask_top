from flask import g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app import db
from utils.decorators import login_required
from flask_restful.inputs import regex
from models.article import Comment, Article


class CommentResource(Resource):
    """发布主评论"""
    method_decorators = {"post": [login_required]}

    """
    发布主评论思路：
        # 1.获取参数
        # 1.1 当前登录用户id: user_id
        # 1.2 发布评论的文章id：target
        # 1.3 评论内容： content
        # 2.参数校验
        # 3.逻辑处理
        # 3.1 新建评论模型对象，保存到数据库
        # 3.2 更新文章的评论数量
        # 3.3 提交到数据库
        # 4.返回值处理

    """

    def post(self):
        # 1.获取参数
        # 1.1 当前登录用户id: user_id
        user_id = g.user_id

        parser = RequestParser()
        parser.add_argument("target", type=int, required=True, location='json')
        parser.add_argument("content", type=regex(r'.+'), required=True, location='json')
        ret = parser.parse_args()
        # 1.2 发布评论的文章id：target
        article_id = ret.target
        # 1.3 评论内容： content
        comment_content = ret.content
        # 2.参数校验

        # 3.逻辑处理
        # 3.1 新建评论模型对象，保存到数据库
        comment_obj = Comment(user_id=user_id,
                              article_id=article_id,
                              content=comment_content,
                              parent_id=0)
        db.session.add(comment_obj)
        # 3.2 更新文章的评论数量
        Article.query.filter(Article.id == article_id) \
            .update({"comment_count": Article.comment_count + 1})

        # 3.3 提交到数据库
        db.session.commit()

        # 4.返回值处理
        return {"com_id": comment_obj.id,
                "target": article_id}
