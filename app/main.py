from app import create_app
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

# 创建开发模式的app对象
app = create_app("dev")


@app.route('/')
def index():
    # 返回所有的路由信息
    # {"视图函数名称": "url路径"}
    rule_dict = {rule.endpoint: rule.rule for rule in app.url_map.iter_rules()}

    # 返回json字符串作为响应
    return jsonify(rule_dict)
