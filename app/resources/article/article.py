from flask import g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from datetime import datetime
from sqlalchemy.orm import load_only
from app import db
from models.article import Article, ArticleContent, Collection, Attitude
from models.user import User, Relation
from utils.constants import HOME_PRE_PAGE


class ArticleDetailResource(Resource):
    """文章详情接口类视图"""

    """
    思路：
        # 1.获取参数
        # 1.1 通过路径传递文章的id： <int: article_id>
        # 1.2 如果有登录，获取登录的用户id： user_id
        # 2.参数校验
        # 3.逻辑处理
        # 3.1 先查询文章详情基本资料
        # 3.2 用户id有值，再去查询文章态度，关注，收藏信息
        # 4.返回值处理
    """

    def get(self, article_id):
        # 1.获取参数
        # 1.1 通过路径传递文章的id： <int: article_id>
        # 1.2 如果有登录，获取登录的用户id： user_id
        # 2.参数校验
        user_id = g.user_id

        # 3.逻辑处理
        # 3.1 先查询文章详情基本资料
        article = db.session.query(Article.id,  # 文章id
                                   Article.title,
                                   Article.ctime,
                                   Article.user_id,  # 作者id
                                   User.name,
                                   User.profile_photo,
                                   ArticleContent.content) \
            .join(User, Article.user_id == User.id) \
            .join(ArticleContent, Article.id == ArticleContent.article_id) \
            .filter(Article.id == article_id).first()

        # 将文章对象序列化成字典
        article_dict = {
            "art_id": article.id,
            "title": article.title,
            "pubdate": article.ctime.isoformat(),  # 时间日期转换成标准日期字符串
            "aut_id": article.user_id,
            "aut_name": article.name,
            "aut_photo": article.profile_photo,
            "content": article.content,
            "is_followed": False,
            "attitude": -1,  # 不喜欢0 喜欢1 无态度-1
            "is_collected": False
        }

        # 3.2 用户id有值，再去查询文章态度，关注，收藏信息
        if user_id:
            # 1.查询当前登录用户是否关注文章作者
            # 查询条件：Relation.user_id == user_id 当前登录的用户是粉丝id
            # 查询条件：Relation.author_id == article.user_id 文章的作者id
            relation = Relation.query.options(load_only(Relation.id)) \
                .filter(Relation.user_id == user_id,
                        Relation.author_id == article.user_id).first()

            # 赋值关注关系
            article_dict["is_followed"] = True if relation else False

            # 2.查询当前登录用户是否收藏当前文章
            collection = Collection.query.options(load_only(Collection.id)) \
                .filter(Collection.user_id == user_id,
                        Collection.article_id == article.id,
                        Collection.is_deleted == False).first()

            # 赋值收藏关系
            article_dict["is_collected"] = True if collection else False

            # 3.查询当前登录用户对文章的态度关系
            attitude_obj = Attitude.query.options(load_only(Attitude.id)) \
                .filter(Attitude.user_id == user_id,
                        Attitude.article_id == article.id).first()  # type: Attitude
            # 用户对文章的态度赋值
            if attitude_obj:
                article_dict["attitude"] = attitude_obj.attitude

        return article_dict


class ArticleListResource(Resource):
    """文章列表页面展示【下拉刷新 上拉加载更多】"""

    """
    思路：
        # 1.获取参数
        # 1.1 时间戳: timestamp
        # 1.2 频道id：channel_id
        # 2.参数校验
        # 3.逻辑处理[增删改查]
        # 3.1 channel_id==0推荐频道返回一个空的数据
        # 3.2 获取文章的基本信息[文章基础数据 + 作者名称] join查询
        # 3.2 查询条件：1.文章的频道id == channel_id  2.查询审核通过的文章 3.查询小于timestamp时间的文章数据
        # 3.3 按照发布时间降序排序 + 分页查询
        # 3.4 文章对象转字典
        # 4.返回响应
        # 4.1 文章基础数据 + pre_timestamp[当页最后一篇文章数据]
    """

    def get(self):
        # 1.获取参数
        # 1.1 时间戳: timestamp
        # 1.2 频道id：channel_id
        # 2.参数校验
        parser = RequestParser()
        parser.add_argument("timestamp", location='args', type=int, required=True)
        parser.add_argument("channel_id", location='args', type=int, required=True)

        # 参数可以允许不传递
        parser.add_argument("per_page", location='args', type=int, default=HOME_PRE_PAGE)

        # 开始解析
        ret = parser.parse_args()
        timestamp = ret.timestamp
        channel_id = ret.channel_id
        per_page = ret.per_page

        # 3.1 channel_id==0推荐频道返回一个空的数据
        if channel_id == 0:
            return {"results": [], "pre_timestamp": 0}

        # 时间戳处理 13位毫秒时间戳 ==> 秒时间戳 ==> 日期
        date = datetime.fromtimestamp((timestamp / 1000))

        # 3.2 获取文章的基本信息[文章基础数据 + 作者名称] join查询
        # 3.2 查询条件：1.文章的频道id == channel_id  2.查询审核通过的文章 3.查询小于timestamp时间的文章数据
        # 3.3 按照发布时间降序排序 + 分页查询
        article_list = db.session.query(Article.id,
                                        Article.title,
                                        Article.user_id,
                                        Article.ctime,
                                        Article.comment_count,
                                        Article.cover,
                                        User.name).join(User, Article.user_id == User.id) \
            .filter(Article.channel_id == channel_id,
                    Article.status == Article.STATUS.APPROVED,
                    Article.ctime < date). \
            order_by(Article.ctime.desc()).limit(per_page).all()

        # 3.4 文章对象转字典
        articles = [{
            "art_id": item.id,
            "title": item.title,
            "aut_id": item.user_id,
            "pubdate": item.ctime.isoformat(),  # 将日期转换成标准日期字符串
            "aut_name": item.name,
            "comm_count": item.comment_count,
            "cover": item.cover
        } for item in article_list]

        # 4.1 文章基础数据 + pre_timestamp[当页最后一篇文章数据]
        # article_list[-1] 最后一篇文章
        # article_list[-1].ctime 文章日期
        # article_list[-1].ctime.timestamp() 10位的秒为单位的时间戳  ==> 毫秒时间戳
        pre_timestamp = int(article_list[-1].ctime.timestamp()) * 1000 if article_list else 0

        return {"results": articles, "pre_timestamp": pre_timestamp}
