from redis import StrictRedis, WatchError

# 1.创建redis客户端对象
redis_cli = StrictRedis(decode_responses=True)
# 2.创建管道对象
pipeline = redis_cli.pipeline()
key = "count"

while True:

    try:
        # 3.查询库存
        count = redis_cli.get(key)
        # 4.使用watch观察字段
        pipeline.watch(key)

        if int(count) > 0:
            # 5.手动开启事务-由于使用管道监听了key，管道此时不会自动开启事务
            pipeline.multi()

            # 6.在事务中执行减库存命令
            pipeline.decr(key)

            # 7.提交事务，提示下单成功
            pipeline.execute()
            print("下单成功")
        else:
            print("库存不足")
            # 重置管道-取消观察字段
            pipeline.reset()
            break
    except WatchError as e:
        # 8.捕获异常处理异常
        print("库存不足： {}".format(e))
        continue
