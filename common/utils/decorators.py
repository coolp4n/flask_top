# 强制登录装饰器
from flask import g
from functools import wraps


def login_required(view_func):
    # 防止装饰器修改被装饰函数名和文档等信息
    @wraps(view_func)
    def wrapper(*args, **kwargs):

        # 从g对象中提取用户user_id
        user_id = g.user_id

        # 1.判断是否有user_id  ==> 未登录
        if user_id is None:
            # 401登录权限认证失败[token过期， token无效， 未携带token]
            # 2小时有效的用户token，访问后端
            return {"message": "invalid user token"}, 401

        # 2.判断是否是刷新token ==> 无效的token，只允许用户token做登录权限认证
        elif user_id is not None and g.is_refresh:
            # 一旦返回403，代表携带的是刷新token
            return {"message": "dont use refresh token for authorization"}, 403

        # 3.user_id有值同时is_refresh=False，携带的是用户token 允许进入视图函数
        else:
            # 进入视图函数
            return view_func(*args, **kwargs)

    return wrapper
