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
        """发布主评论 + 回复子评论"""
        # 1.获取参数
        # 1.1 当前登录用户id: user_id
        user_id = g.user_id

        parser = RequestParser()
        parser.add_argument("target", type=int, required=True, location='json')
        parser.add_argument("content", type=regex(r'.+'), required=True, location='json')
        parser.add_argument("parent_id", type=int, location='json')
        ret = parser.parse_args()
        # 1.2 发布评论的文章id：target
        article_id = ret.target
        # 1.3 评论内容： content
        comment_content = ret.content
        # 1.4 获取父评论id
        parent_id = ret.parent_id

        # 3.逻辑处理
        if parent_id:
            # ===========【回复子评论】=============
            # 创建子评论对象
            comment_obj = Comment(user_id=user_id,
                                  article_id=article_id,
                                  content=comment_content,
                                  parent_id=parent_id)

            # 查询子评论对应的主评论，更新回复评论数量 + 1
            # 主评论：Comment.query.filter(Comment.id == parent_id)
            Comment.query.filter(Comment.id == parent_id).update({"reply_count": Comment.reply_count + 1})

            # 提交数据到数据库
            db.session.add(comment_obj)

            # 注意：需要提交到数据库
            db.session.commit()

            # 返回子评论数据
            return {
                "com_id": comment_obj.id,
                "target": article_id,
                "parent_id": parent_id,
                "mesaage": "回复子评论成功"
            }

        else:
            # ===========【发布主评论】=============
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
                    "target": article_id,
                    "mesaage": "发布主评论成功"}

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
        # 使用type参数区分主、子评论
        # 其中type=a 代表主评论列表
        # 其中type=c 代表子评论列表
        parser.add_argument("type", type=regex(r'[ac]'), location="args", required=True)

        ret = parser.parse_args()
        # 1.1 offset：大于偏移量的评论
        offset = ret.offset
        # 1.2 source = 文章id or 父评论id
        source = ret.source
        # 1.3 limit: 限制条数，分页
        limit = ret.limit
        # 1.4 提取类型
        type = ret.type

        # 3.逻辑处理
        if type == "a":
            # ============【查询主评论列表】===============
            # 3.1 查询评论表中偏移量大于offset的限定条数limit的评论，该评论属于当前article_id文章下的评论
            # TODO: 只查询主评论列表 Comment.parent_id == 0
            # 注意：source 代表文章id
            comments = db.session.query(Comment.id,
                                        Comment.user_id,
                                        User.name,
                                        User.profile_photo,
                                        Comment.ctime,
                                        Comment.content,
                                        Comment.reply_count,
                                        Comment.like_count) \
                .join(User, Comment.user_id == User.id) \
                .filter(Comment.article_id == source,
                        Comment.id > offset, Comment.parent_id == 0).limit(limit).all()

            last_id = comments[-1].id if comments else None

            # 3.4 查询主评论总数量
            total_count = Comment.query.filter(Comment.article_id == source, Comment.parent_id == 0).count()

            # 3.5 查询所有评论最后一条评论的id 作为：end_id
            #  最后一条评论的id, 前端用于判断是否剩余评论, 无值返回None
            end_comment = Comment.query.filter(Comment.article_id == source, Comment.parent_id == 0). \
                order_by(Comment.id.desc()).first()

            end_id = end_comment.id if end_comment else None

        else:
            # ============【查询子评论列表】===============
            # 注意：source 代表 parent_id
            comments = db.session.query(Comment.id,
                                        Comment.user_id,
                                        User.name,
                                        User.profile_photo,
                                        Comment.ctime,
                                        Comment.content,
                                        Comment.reply_count,
                                        Comment.like_count) \
                .join(User, Comment.user_id == User.id) \
                .filter(Comment.id > offset, Comment.parent_id == source).limit(limit).all()

            last_id = comments[-1].id if comments else None

            # 3.4 查询子评论总数量
            total_count = Comment.query.filter(Comment.parent_id == source).count()

            # 3.5 查询所有评论最后一条评论的id 作为：end_id
            #  最后一条评论的id, 前端用于判断是否剩余评论, 无值返回None
            end_comment = Comment.query.filter(Comment.parent_id == source). \
                order_by(Comment.id.desc()).first()

            end_id = end_comment.id if end_comment else None

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

        return {
            "total_count": total_count,
            "last_id": last_id,
            "end_id": end_id,
            "results": comment_dict_list
        }
