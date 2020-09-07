from flask import g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app import db
from models.user import User
from utils.decorators import login_required
from flask_restful.inputs import regex
from models.article import Comment, Article


class CommentResource(Resource):
    """发布主评论  + 评论列表"""
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


    """查询评论列表接口类视图"""
    """
        查询评论列表思路：
            # 1.获取参数
            # 1.1 offset：大于偏移量的评论
            # 1.2 source: article_id
            # 1.3 limit: 限制条数，分页
            # 2.参数校验
            # 3.逻辑处理
            # 3.1 查询评论表中偏移量大于offset的限定条数limit的评论，该评论属于当前article_id文章下的评论
            # 3.2 评论对象转换成字典
            # 3.3 当前页最后一条评论的id， 作为：last_id
            # 3.4 查询评论总数量
            # 3.5 查询所有评论最后一条评论的id 作为：end_id
            # 4.返回值处理
        """

    def get(self):
        # 1.获取参数
        # 2.参数校验
        parser = RequestParser()
        parser.add_argument("offset", type=int, location="args", default=0)
        parser.add_argument("source", type=int, location="args", required=True)
        parser.add_argument("limit", type=int, location="args", default=10)
        ret = parser.parse_args()
        # 1.1 offset：大于偏移量的评论
        offset = ret.offset
        # 1.2 source = 文章id
        source = ret.source
        # 1.3 limit: 限制条数，分页
        limit = ret.limit

        # 3.逻辑处理
        # 3.1 查询评论表中偏移量大于offset的限定条数limit的评论，该评论属于当前article_id文章下的评论
        comments = db.session.query(Comment.id,
                                    Comment.user_id,
                                    User.name,
                                    User.profile_photo,
                                    Comment.ctime,
                                    Comment.content,
                                    Comment.reply_count,
                                    Comment.like_count) \
            .join(User, Comment.user_id == User.id) \
            .filter(Comment.article_id == source, Comment.id > offset).limit(limit).all()

        # 3.2 评论对象转换成字典
        comment_dict_list = [{
            "com_id": item.id,
            "aut_id": item.user_id,
            "aut_name": item.name,
            "aut_photo": item.profile_photo,
            "pubdate": item.ctime.isoformat(),
            "content": item.content,
            "reply_count": item.reply_count,
            "like_count": item.like_count
        } for item in comments]

        # 3.3 当前页最后一条评论的id， 作为：last_id
        # 本次请求最后一条评论的id, 上拉加载更多 作为下次请求的offset, 无值返回None
        # 当前组最后一条评论：comments[-1]
        last_id = comments[-1].id if comments else None

        # 3.4 查询评论总数量
        total_count = Comment.query.filter(Comment.article_id == source).count()

        # 3.5 查询所有评论最后一条评论的id 作为：end_id
        #  最后一条评论的id, 前端用于判断是否剩余评论, 无值返回None
        end_comment = Comment.query.filter(Comment.article_id == source).\
            order_by(Comment.id.desc()).first()
        end_id = end_comment.id if end_comment else None

        return {
            "total_count": total_count,
            "last_id": last_id,
            "end_id": end_id,
            "results": comment_dict_list
        }
