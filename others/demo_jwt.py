import jwt
import base64, os
from datetime import datetime, timedelta
from jwt import PyJWTError


def genrate_jwt():
    """生成jwt"""

    # 1.头部信息
    # 2.载荷信息字典
    payload = {
        "user_id": 666,
        "exp": datetime.utcnow() + timedelta(seconds=30)
    }
    # 3.加密秘钥
    key = base64.b64encode(os.urandom(40)).decode()
    # N3llwTOs2W/D8MQ8wtk8rXwyFFLdzvnr/H0mE4J96+IGf0gl7x5aSQ==
    print(key)

    # 4.生成token
    token = jwt.encode(payload, key, algorithm='HS256').decode()
    print(token)
    return token, key


def decode_jwt(token, key):
    """解析token"""

    try:
        payload = jwt.decode(token, key=key, algorithms='HS256')
        print(payload)
        print(payload["user_id"])
    except PyJWTError as e:
        print(e)
        payload = None

if __name__ == '__main__':
    token, key = genrate_jwt()
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo2NjYsImV4cCI6MTU5OTExODAyN30.uoNKWG1Eq7iZNMFFd44Fvzd6faR9RLKaOAIqH4ud_Zw"
    decode_jwt(token, key)
