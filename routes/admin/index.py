from flask import Blueprint, redirect, url_for, render_template, request, jsonify, session
import sqlite3
import os
from werkzeug.security import check_password_hash

from routes.admin.api import attractions as attr, event, food, manager
from utils.auth import manager_required, api_manager_required

bp = Blueprint('admin', __name__)

bp.register_blueprint(attr.bp, url_prefix="/api/attractions")
bp.register_blueprint(event.bp, url_prefix="/api/event")
bp.register_blueprint(food.bp, url_prefix="/api/food")
bp.register_blueprint(manager.bp, url_prefix="/api/manager")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "database.db")

#登入
@bp.get('/login')
def loginPage():
  return render_template('admin/login.html')

@bp.post("/login")
def login():
  # 資料格式驗證
  try:
    data = request.get_json(force=False)
    if data is None:
      raise ValueError
  except Exception:
    return jsonify({"error":"請傳送正確的json格式資料"}), 400
  # 抓取資料
  account = data.get('account')
  pwd = data.get('pwd')

  if not account or not pwd:
    return jsonify({
      "error": "帳號與密碼不可為空"
    }), 400

  # 驗證帳密
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute(
    "SELECT * FROM manager WHERE account = ?",
    (account,)
  )
  result = cursor.fetchone()
  conn.close()

  if result is None:
    return jsonify({"error":"帳號或密碼錯誤"}),400

  if not check_password_hash(result[2], pwd):
    return jsonify({
      "error": "帳號或密碼錯誤"
    }), 400

  session.permanent = True  # 啟用永久/長期 session 設定
  session["manager_login"] = account

  return jsonify({
    "message": "登入成功",
    "redirect": url_for("web.admin.index")
  })

@bp.get('/logout')
def logout():
  session.clear()
  return redirect(url_for("web.admin.loginPage"))

@bp.get('/')
@manager_required
def index():
  return render_template('admin/index.html',current_type="index")

@bp.get('/api/index')
@api_manager_required
def get_index_data():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  cursor.execute(
    "SELECT account, userName, email, mobile, createTime FROM manager WHERE account = ?",
    (session["manager_login"],)
  )
  managerRow = cursor.fetchone()
  manager = {
    "account": managerRow[0],
    "userName": managerRow[1],
    "email": managerRow[2],
    "mobile": managerRow[3],
    "createTime": managerRow[4]
  }

  cursor.execute("SELECT COUNT(*) FROM event")
  event_count = cursor.fetchone()[0]
  cursor.execute("SELECT COUNT(*) FROM attractions")
  attractions_count = cursor.fetchone()[0]
  cursor.execute("SELECT COUNT(*) FROM food")
  food_count = cursor.fetchone()[0]

  statistics = {
    "event": event_count,
    "attraction": attractions_count,
    "food": food_count
  }

  conn.close()

  return jsonify({
    "message": "資料讀取成功",
    "manager": manager,
    "statistics": statistics
  }), 200

@bp.get('/event/')
@manager_required
def event_list():
  return render_template('admin/event/list.html',current_type="event")

@bp.get('/event/add')
@manager_required
def event_add():
  return render_template('admin/event/add.html',current_type="event")

@bp.get('/event/edit/<int:eventId>')
@manager_required
def event_edit(eventId):
  return render_template('admin/event/edit.html',current_type="event", eventId=eventId)

@bp.get('/attractions/')
@manager_required
def attr_list():
  return render_template('admin/attractions/list.html',current_type="attractions")

@bp.get('/attractions/add')
@manager_required
def attr_add():
  return render_template('admin/attractions/add.html',current_type="attractions")

@bp.get('/attractions/edit/<int:attId>')
@manager_required
def attr_edit(attId):
  return render_template('admin/attractions/edit.html',current_type="attractions", attId=attId)

@bp.get('/food/')
@manager_required
def food_list():
  return render_template('admin/food/list.html',current_type="food")

@bp.get('/food/add')
@manager_required
def food_add():
  return render_template('admin/food/add.html',current_type="food")

@bp.get('/food/edit/<int:foodId>')
@manager_required
def food_edit(foodId):
  return render_template('admin/food/edit.html',current_type="food", foodId=foodId)
