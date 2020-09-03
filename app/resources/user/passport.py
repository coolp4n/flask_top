from flask_restful import Resource
import random
from app import redis_client
from utils.constants import APP_SMSCODE_EXPIRE


class SMSCodesResource(Resource):
    """发送短信验证码的类视图"""

    def get(self, mobile):
        """发送短信验证码"""

        # 1.构建6位随机的短信验证码
        random_code = "%06d" % random.randint(0, 999999)
        # print(random_code)

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
