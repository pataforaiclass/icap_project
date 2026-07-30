# import sqlite3
from flask import Flask, redirect, url_for, render_template
from routes import web

from database import init_db

app = Flask(__name__)
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'
NAV_ITEMS = [
    ("event", "年度活動"),
    ("attr", "熱門景點"),
    ("food", "美食巡禮"),
    ("acco", "旅遊住宿"),
    ("traffic", "交通情報")
]

@app.context_processor
def inject_nav():
  return {
    "nav_items": NAV_ITEMS
  }

app.register_blueprint(web.bp)

# 測試
@app.route("/test")
def test():
  return render_template("test.html")
  # return jsonify({"message":"app is working"})

if __name__ == '__main__':
  initStr = init_db.init_db()
  if initStr:
    print(f" * SQLITE 資料庫已初始化，初始化的資料表：{initStr}")
  app.run(debug=True)