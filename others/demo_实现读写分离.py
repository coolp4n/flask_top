import random
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SignallingSession, get_state, SQLAlchemy
from sqlalchemy import orm
import pymysql
pymysql.install_as_MySQLdb()

# 创建app对象
app = Flask(__name__)

# 即使有了多个数据库的绑定SQLALCHEMY_BINDS，但是真正迁移数据库的时候依赖SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:mysql@192.168.243.154:3306/test37"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_BINDS"] = {
    "master": "mysql://root:mysql@192.168.243.154:3306/test37",  # 主库
    "slave1": "mysql://root:mysql@192.168.243.154:8306/test37",  # 从库
    "slave2": "mysql://root:mysql@192.168.243.154:3306/test37",  # 从库
}


# 第一步
# 1. 自定义Session类, 继承SignallingSession, 并重写get_bind方法
class RoutingSession(SignallingSession):
    def __init__(self, *args, **kwargs):
        super(RoutingSession, self).__init__(*args, **kwargs)

    def get_bind(self, mapper=None, clause=None):
        # 全局变量
        state = get_state(self.app)
        if mapper is not None:
            try:
                # SA >= 1.3
                persist_selectable = mapper.persist_selectable
            except AttributeError:
                # SA < 1.3
                persist_selectable = mapper.mapped_table

            info = getattr(persist_selectable, 'info', {})
            bind_key = info.get('bind_key')
            if bind_key is not None:
                return state.db.get_engine(self.app, bind=bind_key)
        # 读取SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@192.168.243.154:3306/test37", 数据库引擎返回
        # return SessionBase.get_bind(self, mapper, clause)
        # 实现读写分离
        from sqlalchemy.sql.dml import UpdateBase
        # 实现读写分离
        # self._flushing == True 写操作或者删除更新操作-访问主数据库
        if self._flushing or isinstance(clause, UpdateBase):
            print("写，删除 更新 访问主数据库")
            return state.db.get_engine(self.app, bind="master")
        else:
            # 读操作-访问从数据库
            slave_name = random.choice(["slave1", "slave2"])
            print("读操作 - 访问从数据库: ", slave_name)
            return state.db.get_engine(self.app, bind=slave_name)


# 第二步
# 2. 自定义SQLALchemy类, 重写create_session方法
class RoutingSQLAlchemy(SQLAlchemy):
    def create_session(self, options):
        # 继承-拓展SQLAlchemy的功能，封装一个RoutingSession类实现读写分离
        return orm.sessionmaker(class_=RoutingSession, db=self, **options)


# 第三步
db = RoutingSQLAlchemy(app)

# 构建模型类
class User(db.Model):
    __tablename__ = 't_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    age = db.Column(db.Integer, default=0, index=True)


@app.route('/')
def index():
    """增加数据"""
    # write1()
    # read()
    # read()
    update()
    return "index"


def read():
    print('---读-----------')
    # 触发任意一个从库
    users = User.query.all()
    print(users)
    for user in users:
        print(user.id, user.name, user.age)


def write():
    print('---写-----------')
    # 触发主库
    user1 = User(name='james', age=20)
    db.session.add(user1)
    db.session.commit()

def write1():
    print('---写1-----------')
    # 触发主库
    user1 = User(name='curry', age=30)
    db.session.add(user1)
    db.session.commit()


def update():
    print("---更新写---")
    # 触发主库
    User.query.filter(User.name == 'james').update({"name": "kobe"})
    db.session.commit()


if __name__ == '__main__':
    # 重置所有继承自db.Model的表
    # 如果模型类没有设置__bind_ky__属性(指定对应的数据库), 则DDL操作 根据SQLALCHEMY_DATABASE_URI 指定的数据库进行处理
    # db.drop_all()
    # db.create_all()
    app.run(debug=True, port=8888)
