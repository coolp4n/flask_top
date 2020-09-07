import random
from flask_sqlalchemy import SignallingSession, get_state, SQLAlchemy
from sqlalchemy import orm


# 1. 自定义Session类, 继承SignallingSession, 并重写get_bind方法
class RoutingSession(SignallingSession):
    def __init__(self, *args, **kwargs):
        super(RoutingSession, self).__init__(*args, **kwargs)
        # 问题：每次db.session都会触发数据库选择效率低
        # 方案：数据库选择方法在init方法中
        # 随机选择从数据库的key
        self.slave_key = random.choice(["slave1", "slave2"])

    def get_bind(self, mapper=None, clause=None):
        """每次数据库操作(增删改查及事务操作)都会调用该方法, 来获取对应的数据库引擎(访问的数据库)"""
        state = get_state(self.app)
        if mapper is not None:
            try:
                # SA >= 1.3
                persist_selectable = mapper.persist_selectable
            except AttributeError:
                # SA < 1.3
                persist_selectable = mapper.mapped_table
            # 如果项目中指明了特定数据库，就获取到bind_key指明的数据库，进行数据库绑定
            info = getattr(persist_selectable, 'info', {})
            bind_key = info.get('bind_key')
            if bind_key is not None:
                return state.db.get_engine(self.app, bind=bind_key)

        # 使用默认的主数据库
        # return SessionBase.get_bind(self, mapper, clause)

        from sqlalchemy.sql.dml import UpdateBase
        # 如果模型类未指定数据库, 判断是否为写操作
        # delete和update不会触发_flushing
        # isinstance(clause, UpdateBase) 判断数据库操作行为，clause如果是增删改查都是属于UpdateBase子类
        if self._flushing or isinstance(clause, UpdateBase):
            # 写操作--主数据库
            print("写操作--主数据库")
            return state.db.get_engine(self.app, bind="master")

        else:
            # 读操作--从数据库
            print("读操作--从数据库: ", self.slave_key)
            return state.db.get_engine(self.app, bind=self.slave_key)


# 2. 自定义SQLALchemy类, 重写create_session方法
class RoutingSQLAlchemy(SQLAlchemy):
    def create_session(self, options):
        # 继承-拓展SQLAlchemy的功能，封装一个RoutingSession类实现读写分离
        return orm.sessionmaker(class_=RoutingSession, db=self, **options)
