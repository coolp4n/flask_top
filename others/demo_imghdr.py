import imghdr

# 方案1：
type = imghdr.what("./mz2.jpg")
print(type)

# 方案2：
with open('./mz2.jpg', 'rb') as f:
    type2 = imghdr.what(None, f.read())
    print(type2)
