from flask import Flask
from .settings.config import config_dict
import sys
import os

# 2.将common添加到系统搜索路径中
# /Users/chenqian/Desktop/深圳37期Flask项目/HMTopNews
# 当前路径的上一层路径
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# # /Users/chenqian/Desktop/深圳37期Flask项目/HMTopNews/common
sys.path.insert(0, BASE_PATH + "/common")
from utils.constants import EXTRA_ENV_COINFIG


# from common.utils.constants import EXTRA_ENV_COINFIG


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

    # 2.初始化组件
    # TODO:组成蓝图的初始化组件

    return app
