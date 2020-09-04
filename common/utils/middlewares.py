# 利用请求钩子，在执行视图函数之前，统一提取用户身份
from flask import request, current_app, g
from utils.jwt_util import verify_jwt


# @app.before_rquest
def get_userinfo():
    # 1.用户通过请求头携带token
    # 规定：前端携带token是通过请求头中的: Authorization字段携带
    # 提取请求头中的token信息

    # 用户token user1=token
    token = request.headers.get("Authorization")
    secret = current_app.config['JWT_SECRET']

    """
    用户token:  g.user_id = 1
               g.is_refresh = False
               
    只有用户token才能做登录权限认证        
               
    
    刷新token： g.user_id = 1
               g.is_refresh = True
    
    刷新token只是在用户token过期之后，请求一个新的用户token， 不能用来做权限认证
    """

    g.user_id = None
    g.is_refresh = False

    # token校验，获取载荷字典
    if token:
        payload = verify_jwt(token, secret=secret)
        if payload:
            # 提取用户的信息，保存到g变量中，在本次请求内，就能够g对象中提取到用户信息
            g.user_id = payload.get("user_id")
            g.is_refresh = payload.get("is_refresh")
