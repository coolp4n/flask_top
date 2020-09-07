from datetime import datetime
from sqlalchemy.dialects.mysql import DATETIME
from app import db


class Channel(db.Model):
    """
    新闻频道
    """
    __tablename__ = 'news_channel'

    id = db.Column(db.Integer, primary_key=True, doc='频道ID')
    name = db.Column(db.String(30), doc='频道名称')
    is_default = db.Column(db.Boolean, default=False, doc='是否默认')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class UserChannel(db.Model):
    """
    用户关注频道表
    """
    __tablename__ = 'news_user_channel'

    id = db.Column(db.Integer, primary_key=True, doc='主键ID')
    user_id = db.Column(db.Integer, doc='用户ID')
    channel_id = db.Column(db.Integer, doc='频道ID')
    sequence = db.Column(db.Integer, default=0, doc='序号')
    is_deleted = db.Column(db.Boolean, default=False, doc='是否删除')


class Article(db.Model):
    """
    文章基本信息表
    """
    __tablename__ = 'news_article_basic'

    class STATUS:
        DRAFT = 0  # 草稿
        UNREVIEWED = 1  # 待审核
        APPROVED = 2  # 审核通过
        FAILED = 3  # 审核失败
        DELETED = 4  # 已删除
        BANNED = 5  # 封禁

    id = db.Column(db.Integer, primary_key=True, doc='文章ID')
    user_id = db.Column(db.Integer, doc='用户ID')
    channel_id = db.Column(db.Integer, doc='频道ID')
    title = db.Column(db.String(130), doc='标题')
    cover = db.Column(db.JSON, doc='封面')
    ctime = db.Column(DATETIME(fsp=3), default=datetime.now, doc='创建时间')
    status = db.Column(db.Integer, default=0, doc='帖文状态')
    # 注意：发布评论成功，需要将评论数量自增
    comment_count = db.Column(db.Integer, default=0, doc='评论数')


class ArticleContent(db.Model):
    """
    文章内容表
    """
    __tablename__ = 'news_article_content'

    article_id = db.Column(db.Integer, primary_key=True, doc='文章ID')
    content = db.Column(db.Text, doc='帖文内容')


class Attitude(db.Model):
    """
    文章态度表
    """
    __tablename__ = 'news_attitude'

    class ATTITUDE:
        DISLIKE = 0  # 不喜欢
        LIKING = 1  # 喜欢
        DELETE = -1  # 无态度

    id = db.Column(db.Integer, primary_key=True, doc='主键ID')
    user_id = db.Column(db.Integer, doc='用户ID')
    article_id = db.Column(db.Integer, doc='文章ID')
    attitude = db.Column(db.Integer, doc='态度')


class Collection(db.Model):
    """
    用户收藏表
    """
    __tablename__ = 'news_collection'

    id = db.Column(db.Integer, primary_key=True, doc='主键ID')
    user_id = db.Column(db.Integer, doc='用户ID')
    article_id = db.Column(db.Integer, doc='文章ID')
    is_deleted = db.Column(db.Boolean, default=False, doc='是否删除')


class Comment(db.Model):
    """
    文章评论
    """
    __tablename__ = 'news_comment'

    id = db.Column(db.Integer, primary_key=True, doc='评论ID')
    user_id = db.Column(db.Integer, doc='用户ID')
    article_id = db.Column(db.Integer, doc='文章ID')
    parent_id = db.Column(db.Integer, doc='被评论的评论id')
    reply_count = db.Column(db.Integer, default=0, doc='回复数')
    ctime = db.Column(db.DateTime, default=datetime.now, doc='创建时间')
    like_count = db.Column(db.Integer, default=0, doc='点赞数')
    content = db.Column(db.String(200), doc='评论内容')
