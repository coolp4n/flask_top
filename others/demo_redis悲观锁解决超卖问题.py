from redis import StrictRedis

# 1.创建客户端对象
redis_cli = StrictRedis(decode_responses=True)

# 锁的键名称
key = "order:lock"

while True:
    # 2.争夺锁资源
    lock = redis_cli.setnx(key, 11)

    # 3.获取锁资源的redis客户端对象有资格下单，否则在等待
    if lock:

        # 防止忘记移除锁资源出现死锁状况，给锁添加有效期
        redis_cli.expire(key, 5)

        # 4.查询库存
        count = redis_cli.get("count")
        if int(count) > 0:
            # 5.减库存，下单成功
            redis_cli.decr("count")
            print("下单成功")
        # 6.库存不足
        else:
            print("库存不足")

        # 7.移除锁资源
        redis_cli.delete(key)
        break
