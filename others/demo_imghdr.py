import imghdr

pic_path = r'C:\Users\xinpa\Pictures\姐姐\微信图片_20211008215854.jpg'
# 方案1：
type = imghdr.what(pic_path)
print(type)

# 方案2：
with open(pic_path, 'rb') as f:
    type2 = imghdr.what(None, f.read())
    print(type2)
