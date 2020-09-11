from redis import StrictRedis

# 创建redis客户端对象
redis_cli = StrictRedis(decode_responses=True)

# 创建管道对象--管道对象保存执行命令默认就会开启事务
pipe = redis_cli.pipeline()

# 利用管道对象对数据库进行增删改查
a = pipe.set("user1", "xiaoming")
b = pipe.get("user1")

# 执行管道中命令-提交事务
c = pipe.execute()

print(a)
print(b)
print(c)




