from redis import StrictRedis

# 1.创建redis客户端对象
redis_cli = StrictRedis(decode_responses=True)

# 2.创建管道对象（非事务性管道）
# transaction=False 只使用管道功能，不会开启事务
pipeline = redis_cli.pipeline(transaction=False)

# 3.执行多条命令
pipeline.set("name", "xiaoming")
pipeline.set("age", 18)

# 4. 提交命令
ret = pipeline.execute()

print(ret)
