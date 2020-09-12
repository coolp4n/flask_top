from redis import StrictRedis

cli = StrictRedis()
user_dict = {'id': 6, 'name': '18511112222', 'photo': 'http://qg457zgw6.hn-bkt.clouddn.com/FpIa10YMbJkXIB77-HF4Fvt-sxek', 'intro': "", 'art_count': 0, 'follow_count': 1, 'fans_count': 0}

cli.hmset("user:888:basic", user_dict)

print(cli.hgetall("user:888:basic"))
