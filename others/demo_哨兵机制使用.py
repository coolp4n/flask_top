from redis.sentinel import Sentinel
from redis import StrictRedis

# 1.准备哨兵的连接信息[centeros哨兵]
sentinel_host = [
    ("192.168.243.155", 26380),
    ("192.168.243.155", 26381),
    ("192.168.243.155", 26382),
]

# 2.根据连接信息创建哨兵客户端对象
sentinel_cli = Sentinel(sentinel_host)

# 3.准备哨兵监听的主从的别名
server_name = "mymaster"

# 4.根据别名分别获取redis主数据、redis从数据库
redis_master = sentinel_cli.master_for(server_name, decode_responses=True)
redis_slave = sentinel_cli.slave_for(server_name, decode_responses=True)

# 5.读写操作[主数据库]
redis_master.set("user6", "james")
print(redis_master.get("user6"))

# 从数据库只能读取
print(redis_slave.get("user6"))
