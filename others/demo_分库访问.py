from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 添加数据库配置
# 单库访问
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:mysql@192.168.243.154:3306/db1"

# 多库访问
app.config["SQLALCHEMY_BINDS"] = {
    "db1": "mysql+pymysql://root:mysql@192.168.243.154:3306/db1",
    "db2": "mysql+pymysql://root:mysql@192.168.243.154:3306/db2",
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# 执行sql语句输出
app.config["SQLALCHEMY_ECHO"] = True

# 创建数据库对象
db = SQLAlchemy(app)


# 创建模型类
# 指定User表保存在db1数据库中  一
class User(db.Model):
    __tablename__ = "t_user"
    # 绑定指定数据库
    __bind_key__ = 'db1'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


# 地址表   存储在db2中    多
class Address(db.Model):
    __tablename__ = 't_adr'
    # 设置表所在的数据库URI
    __bind_key__ = 'db2'
    id = db.Column(db.Integer, primary_key=True)
    detail = db.Column(db.String(20), unique=True)
    user_id = db.Column(db.Integer)


@app.route('/')
def hello_world():
    # 添加数据
    user1 = User(name="kobe")
    db.session.add(user1)
    # 注意：情况会话层缓存，执行sql，生成用户id，但是未写入数据库
    db.session.flush()
    ad1 = Address(detail="洛杉矶", user_id=user1.id)
    ad2 = Address(detail="深圳", user_id=user1.id)
    db.session.add_all([ad1, ad2])

    # 2020-09-09 10:08:38,892 INFO sqlalchemy.engine.base.Engine COMMIT
    # 2020-09-09 10:08:38,894 INFO sqlalchemy.engine.base.Engine COMMIT
    # 虽然代码层面只有一次v提交操作，但是sql语句层面，底层会分别根据不同的数据库对应不同的表，做两次提交操作
    db.session.commit()
    return 'Hello World!'


@app.route('/select')
def select():
    # 查询kobe对应所有地址信息
    # TODO:join查询，也是不支持夸库查询
    # 分开来查询，先查询用户表，再查询地址表
    user = User.query.filter(User.name == "kobe").first()

    # 根据用户id查询地址信息
    adds = Address.query.filter(Address.user_id == user.id)
    for ad in adds:
        print(ad.detail)
    return "select success"


if __name__ == '__main__':
    # 如果没有在模型类中指定__bind_key__ 数据库别名，那么就按照SQLALCHEMY_DATABASE_URI指定的数据库进行创建、删除表
    # 如果在模型类中指定了__bind_key__ 数据库别名，就按照指定的数据库连接信息删除、创建数据库表
    # db.drop_all()
    # db.create_all()
    app.run(debug=True, port=5002)
