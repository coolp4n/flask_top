from rediscluster import RedisCluster

# 1.准备集群的连接信息[centeros]
# 一般情况连接信息是带有卡槽的三个主数据库的连接信息
startup_nodes = [
    {"host": "192.168.243.155", "port": 7000},
    {"host": "192.168.243.155", "port": 7001},
    {"host": "192.168.243.155", "port": 7002},
]

# 2.创建集群客户端对象
# 支持写一个集群的ip和端口，就能找到整个集群中的所有数据库
# 支持以列表的形式填写多个集群的ip和端口
# decode_responses=True 将bytes数据转换成字符串
cluster_cli = RedisCluster(startup_nodes=startup_nodes)

# 3.使用集群进行数据增删改查
# cluster_cli.set("user2", "kobe666")
# print(cluster_cli.get("user2"))


user_dict = {'id': 7, 'name': '18511112221', 'photo': 'http://qg457zgw6.hn-bkt.clouddn.com/FpIa10YMbJkXIB77-HF4Fvt-sxek', 'intro': "", 'art_count': 0, 'follow_count': 1, 'fans_count': 0}

cluster_cli.hmset("user:7777:basic", user_dict)

print(cluster_cli.hgetall("user:7777:basic"))
