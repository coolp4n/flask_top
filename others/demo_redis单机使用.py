from redis import StrictRedis

# 1.redis客户端对象  [redis-cli命令进入客户端]
# decode_responses=True redis默认会将数据转换成bytes类别二进制编码存储，取出的时候将bytes=>string
redis_cli = StrictRedis(host="192.168.243.154", port=6381, decode_responses=True)

# 2.数据增删改查
redis_cli.set("name", "xiaoming", ex=3600)
print(redis_cli.get("name"))

# 3.hash类型
redis_cli.hmset("user:1", {"name": "curry", "age": 18})
print(redis_cli.hmget("user:1", ["name", "age"]))
