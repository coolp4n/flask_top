from flask import Blueprint
from utils.constants import USER_URL_PREFIX
from flask_restful import Api
from utils.output import output_json
from .channel import AllChannelResource
from .article import ArticleListResource, ArticleDetailResource

# 1.创建文章蓝图对象
article_bp = Blueprint("article_bp", __name__, url_prefix=USER_URL_PREFIX)

# 2.将蓝图对象包装成具备restful风格api对象
article_api = Api(article_bp)

# 3.自定义返回json格式
article_api.representation(mediatype='application/json')(output_json)

# 4.给类视图添加路由信息
# /app/channels
article_api.add_resource(AllChannelResource, '/channels')
# /app/articles
article_api.add_resource(ArticleListResource, '/articles')
# /app/articles/article_id
article_api.add_resource(ArticleDetailResource, '/articles/<int:article_id>')
