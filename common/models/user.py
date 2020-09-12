from app import db
from datetime import datetime


class User(db.Model):
    """
    用户基本信息
    """
    __tablename__ = 'user_basic'

    id = db.Column(db.Integer, primary_key=True, doc='用户ID')
    mobile = db.Column(db.String(11), doc='手机号')
    name = db.Column(db.String(20), doc='昵称')
    last_login = db.Column(db.DateTime, doc='最后登录时间')
    introduction = db.Column(db.String(50), doc='简介')
    article_count = db.Column(db.Integer, default=0, doc='作品数')
    following_count = db.Column(db.Integer, default=0, doc='关注的人数')
    fans_count = db.Column(db.Integer, default=0, doc='粉丝数')
    profile_photo = db.Column(db.String(130), doc='头像')

    def to_dict(self):
        """模型转字典, 用于序列化处理"""

        return {
            'id': self.id,
            'name': self.name,
            'photo': self.profile_photo,
            # 注意：redis不支持None类型 但是支持空字符串
            'intro': self.introduction if self.introduction else "",
            'art_count': self.article_count,
            'follow_count': self.following_count,
            'fans_count': self.fans_count
        }


class Relation(db.Model):
    """
    用户关系表
    """
    __tablename__ = 'user_relation'

    class RELATION:
        # 取消关注
        DELETE = 0
        # 关注
        FOLLOW = 1
        # 拉黑
        BLACKLIST = 2

    id = db.Column(db.Integer, primary_key=True, doc='主键ID')
    user_id = db.Column(db.Integer, doc='用户ID')  # 粉丝id
    author_id = db.Column(db.Integer, doc='目标用户ID')  # 作者id
    relation = db.Column(db.Integer, doc='关系')
    update_time = db.Column(db.DateTime, default=datetime.now, doc='更新时间')
