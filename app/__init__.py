from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .settings.config import config_dict
import sys
import os
from redis import StrictRedis
from flask_migrate import Migrate

# 2.将common添加到系统搜索路径中
# /Users/chenqian/Desktop/深圳37期Flask项目/HMTopNews
# 当前路径的上一层路径
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# # /Users/chenqian/Desktop/深圳37期Flask项目/HMTopNews/common
sys.path.insert(0, BASE_PATH + "/common")
from utils.constants import EXTRA_ENV_COINFIG

# from common.utils.constants import EXTRA_ENV_COINFIG

# 创建db数据库对象，此时还未绑定Flask应用
# 暴露给其他模块调用
db = SQLAlchemy()

# redis客户端对象暴露给其他模块调用, 并且声明其类型为StrictRedis的对象
redis_client = None  # type:StrictRedis


# 1.定义工厂函数，生产app对象
def create_flask_app(type):
    # 1.创建应用对象
    app = Flask(__name__)

    # 2.加载配置类中配置信息
    config_class = config_dict[type]
    app.config.from_object(config_class)

    # 3.加载环境变量中的隐私配置
    # silent=True 加载失败也不会报错
    app.config.from_envvar(EXTRA_ENV_COINFIG, silent=True)

    return app


# 给外界调用的工厂函数
def create_app(type):
    """创建app对象 初始化组件"""

    # 1.创建app对象
    app = create_flask_app(type)

    # 2.注册拓展信息组件化
    register_extensions(app)

    # 3.注册蓝图的初始化组件
    register_bluprint(app)

    return app


def register_bluprint(app: Flask):
    # 注册user模块的蓝图对象
    # 防止循环导包：cannot import x_module
    # 延后导包，懒加载，用到的时候再导包
    from app.resources.user import user_bp
    # 注册蓝图
    app.register_blueprint(user_bp)

    # 注册自定义转换器类
    # app.url_map.converters["key"] = classNAME


def register_extensions(app: Flask):
    # 4.延迟绑定app对象和db数据库对象
    db.init_app(app)

    # 5.延迟初始化redis客户端对象
    # decode_responses=True 将响应进行解析-bytes转换成字符串
    # 将局部变量声明为全局变量
    global redis_client
    redis_client = StrictRedis(host=app.config["REDIS_HOST"],
                               port=app.config["REDIS_PORT"],
                               decode_responses=True)

    # TODO：注意：先自定义转换器，再注册蓝图，因为蓝图注册的时候就用到了自定义的转换器
    # 添加自定义转换器组件
    from utils.converters import register_converters
    register_converters(app)

    # 数据库迁移
    Migrate(app, db)

    # 注意：需要让Flask项目知道有user.py文件的存在，同时按照文件中定义的模型类进行表的迁移
    from models import user

    # 给get_userinfo添加before_request装饰器
    # 在请求进入视图函数之前，统一提取用户token信息
    from utils.middlewares import get_userinfo
    app.before_request(get_userinfo)

    from flask_cors import CORS
    # 允许跨域请求
    # app 允许跨域的后端app
    # supports_credentials=True 允许跨域访问时携带cookie或者证书token
    # origins=["http://127.0.0.1:5000"] 允许前端那个网站跨域访问后端， 默认：所有网站都可以访问
    # methods = [GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE] 允许所有请求跨域访问
    CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5000"])
