from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from others.db_routing.routing_sqlalchemy import RoutingSQLAlchemy
import pymysql

pymysql.install_as_MySQLdb()
app = Flask(__name__)

# 数据库配置信息
# 绑定单库
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:mysql@192.168.243.154:3306/db_b"
# 绑定多库
app.config["SQLALCHEMY_BINDS"] = {
    "db_a": "mysql://root:mysql@192.168.243.154:3306/db_a",
    "db_b": "mysql://root:mysql@192.168.243.154:3306/db_b",

}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# 数据库对象
# 此刻数据库对象能实现： 1.读写分离   2.根据__bind_key__指定数据库查询  3.定向查询
db = RoutingSQLAlchemy(app)



# 构建模型类
class User(db.Model):
    __tablename__ = 't_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column('username', db.String(20))
    age = db.Column(db.Integer, default=0, index=True)


@app.route('/')
def hello_world():
    # 需求：查询年龄为18岁所有数据： 各个数据库依次遍历查询[水平分表分库]

    # <class 'sqlalchemy.orm.scoping.scoped_session'> 本质：SignallingSession
    print(type(db.session))
    # RoutingSession的对象
    print(type(db.session()))

    # 遍历各个数据库，依次查询满足条件的用户数据
    for db_name in ["db_a", "db_b"]:
        users = db.session().usering_bind(db_name).query(User.name).filter(User.age == 18).all()
        for user in users:
            print(user.name)

    # 注意：如果不清空内部的self._bind只会去最后绑定db_b中查询
    # 这样就不会再按照定向查询的方式去查询数据库
    db.session().usering_bind(None)

    # 再查询数据
    user_List = User.query.filter(User.age == 18)
    for user in user_List:
        print("======", user.name)
    return 'Hello World!'


if __name__ == '__main__':
    # 根据SQLALCHEMY_DATABASE_URI指定的uri地址创建数据库表
    # db.drop_all()
    # db.create_all()
    app.run(debug=True, port=5003)
