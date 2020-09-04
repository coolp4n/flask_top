from qiniu import Auth, put_file, etag, put_data
import qiniu.config
from flask import current_app


def upload_file(data):
    """
    上传图片二进制数据到七牛云
    :param data: 图片二进制数据
    :return:
    """
    # 需要填写你的 Access Key 和 Secret Key
    # 作用：区分是否为七牛云的开发者，权限认证
    access_key = current_app.config["QINIU_ACCESS_KEY"]
    secret_key = current_app.config["QINIU_SECRET_KEY"]

    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间-修改成自己创建的空间名称
    bucket_name = current_app.config["QINIU_BUCKET_NAME"]

    # 上传后保存的文件名
    # 如果图片名称为None,七牛云会根据图片数据按照哈希函数生成一个唯一的图片名称【去重】
    # 同一个文件的哈希值是不变的
    key = None

    # 生成上传 Token，可以指定过期时间等 jwt  3600 一小时有效期
    token = q.upload_token(bucket_name, key, 3600)

    # 要上传文件的本地路径
    # localfile = './mz2.jpg'

    # 上传图片到七牛云
    # 方案1：路径方式上传图片
    # ret, info = put_file(token, key, localfile)

    # 方案2：以二进制图片数据方式上传
    ret, info = put_data(token, key, data)

    if info.status_code == 200:
        # 上传图片成功
        # ret["key"] 提取图片名称
        url_prefix = current_app.config["QINIU_DOMAIN"]
        pic_name = ret["key"]
        full_url = url_prefix + pic_name
        # 返回图片名称和完整url地址
        return pic_name, full_url
    else:
        # 工具类里面的异常信息，需要抛出，不能私自处理,否则调用者不知如何处理异常
        raise BaseException(info.exception)


if __name__ == '__main__':
    with open("/Users/chenqian/Desktop/深圳37期Flask项目/HMTopNews/others/c1.png", 'rb') as f:
        # 注意:需要单独使用需要开启上下文
        # with app.app_context():
        data = f.read()
        url = upload_file(data)
        print(url)
