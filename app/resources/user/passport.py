from flask_restful import Resource
import random
from app import redis_client, db
from models.user import User
from utils.constants import APP_SMSCODE_EXPIRE
from datetime import datetime, timedelta
from flask import current_app, g
from utils.jwt_util import generate_jwt, verify_jwt
from flask_restful.reqparse import RequestParser
from utils.parser import mobile
from flask_restful.inputs import regex
from sqlalchemy.orm import load_only


class SMSCodesResource(Resource):
    """发送短信验证码的类视图"""

    def get(self, mobile):
        """发送短信验证码"""

        # 1.构建6位随机的短信验证码
        random_code = "%06d" % random.randint(0, 999999)
        # print(random_code)
        random_code = "123456"
        # 2.将短信验证码存储到redis数据库
        # app:code:1851111222  123456
        code_key = "app:code:{}".format(mobile)
        # 抽取常量
        redis_client.setex(name=code_key, time=APP_SMSCODE_EXPIRE, value=random_code)

        # 3.调用第三方模块发送短信验证
        print("短信验证码：手机号码：{}  code: {}".format(mobile, random_code))

        # 4.返回响应
        return {"mobile": mobile, "codes": random_code}


"""
自定义返回的json格式
{
    "message": "OK or Error message"，
    "data": 真正数据
}
"""


class LoginRegisterResource(Resource):
    """登录注册视图类"""

    def _genrateJWT(self, user_id):
        """
        生成2小时有效的用户token，和14天有效的刷新token
        :param user_id: 用户id
        :return:
        """

        # 1.生成用户token
        # 1.1 构建载荷信息
        user_payload = {
            "user_id": user_id,
            "is_refresh": False

        }
        # 过期时长-2小时
        expiry = datetime.utcnow() + timedelta(hours=current_app.config["JWT_USER_EXPIRE"])

        # 1.2 获取秘钥
        secret = current_app.config['JWT_SECRET']

        # 1.3 调用工具类生成token
        # TODO:专门用户登录权限验证的token
        token = generate_jwt(user_payload, expiry=expiry, secret=secret)

        # 2. 生成刷新token
        # 1.1 构建载荷信息
        refresh_payload = {
            "user_id": user_id,
            "is_refresh": True
        }
        # 过期时长-14天
        expiry_14day = datetime.utcnow() + timedelta(days=current_app.config["JWT_REFRESH_EXPIRE"])

        # 1.2 获取秘钥
        secret = current_app.config['JWT_SECRET']

        # 1.3 调用工具类生成token
        # TODO: 专门用于：当2小时的用户token过期之后，
        # 在用户无感知的情况下，使用该refresh_token进行刷新请求，获取一个新的2小时有效token
        refresh_token = generate_jwt(refresh_payload, expiry=expiry_14day, secret=secret)

        # 401 token过期==> 前端工作人员 ==>refresh_token ==> 发给后端put ==>返回一个2小时有效的token
        # 403 刷新token也过期了 当刷新token，14天过期后，只能重新登录
        return token, refresh_token

    def post(self):
        """
        # 1.获取参数
        # 1.1 mobile 手机号码
        # 1.2 smscode 短信验证码
        # 2.解析参数
        # 构建解析对象
        # 解析对象添加参数
        # 开始解析
        # 提取解析结果
        # 3.业务逻辑
        # 3.1 根据手机号码去redis数据库取出真实的短信验证码 real_smscode
        # 3.2 短信验证码是否有值，是否和用户填写的短信验证码一致
        # 3.3 一致：根据手机号码查询数据库，是否账号是否存在
        # 3.4 账号存在：直接登录，修改最近一次登录时间，
        # 3.5 账号不存在：直接注册，创建新的用户对象，添加到数据库
        # 4.返回值处理
        # 4.1 返回用户token和refresh_token
        """

        # 1.获取参数
        # 2.解析参数
        # 构建解析对象
        parser = RequestParser()
        # 解析对象添加参数
        parser.add_argument("mobile",
                            required=True,
                            location='json', type=mobile)

        parser.add_argument("code",
                            required=True,
                            location='json', type=regex(r'\d{6}'))

        # 开始解析
        ret = parser.parse_args()
        # 提取解析结果
        # 手机号码 string
        phone = ret["mobile"]
        # 短信验证码
        smscode = ret["code"]

        # 3.业务逻辑
        # 3.1 根据手机号码去redis数据库取出真实的短信验证码 real_smscode
        redis_key = "app:code:{}".format(phone)
        real_smscode = redis_client.get(redis_key)
        # 3.2 短信验证码是否有值，是否和用户填写的短信验证码一致
        # 注意： "123456"  b'123456' decode_responses=True
        if real_smscode is None or real_smscode != smscode:
            return {"message": "invalid sms_code"}, 400

        # 3.3 一致：根据手机号码查询数据库，是否账号是否存在
        # load_only 优化查询
        # 查询-从库
        user = User.query.options(load_only(User.id)).filter(User.mobile == phone).first()

        if user is None:
            # 3.4 账号不存在：直接注册，创建新的用户对象，添加到数据库
            user = User(name=phone, mobile=phone, last_login=datetime.now())
            # 写-主库
            db.session.add(user)
        else:
            # 3.5 账号存在：直接登录，修改最近一次登录时间，
            user.last_login = datetime.now()

        # TODO:最后完成提交操作
        # 写--主库
        db.session.commit()

        # 4.返回值处理
        # 查 --从库
        token, refresh_token = self._genrateJWT(user.id)
        # 4.1 返回用户token和refresh_token
        return {"token": token, "refresh_token": refresh_token}, 201

    def put(self):
        """刷新token请求"""

        # 判断提交的token是刷新token
        user_id = g.user_id
        is_refresh = g.is_refresh
        # 刷新token有效
        if user_id and is_refresh:

            # 重新生成一个新的2小时有效的token
            token, _ = self._genrateJWT(user_id)
            return {"new_token": token}, 201
        else:
            # 刷新token失效了-必须重新登录
            return {"message": "invalid refresh token"}, 403
