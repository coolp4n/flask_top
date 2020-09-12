import pybloomfilter


def get_user_info(user_id):
    # 1.创建布隆过滤器对象
    # filter = pybloomfilter.BloomFilter("布隆过滤器容器大小", "误差率", "文件名称")
    filter = pybloomfilter.BloomFilter(10000000, 0.001, "word.bloom")

    # 2.往过滤器对象中添加可能字段
    id_list = [i for i in range(1, 1000)]
    filter.update(id_list)

    # 3.过滤
    if user_id not in filter:
        print("数据id未包含在过滤器中")
        return None

    # 代表数据包含在过滤器中
    # 执行数据库的增删改查业务逻辑
    print("包含：user_id: ", user_id)


if __name__ == '__main__':
    get_user_info(3000)
