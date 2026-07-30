from flask import Blueprint, redirect, url_for, render_template, request, jsonify, session
import sqlite3
from routes.admin.api import attractions as attr, event, food, manager

bp = Blueprint('admin', __name__)

bp.register_blueprint(attr.bp, url_prefix="/api/attr")
bp.register_blueprint(event.bp, url_prefix="/api/event")
bp.register_blueprint(food.bp, url_prefix="/api/food")
bp.register_blueprint(manager.bp, url_prefix="/api/manager")

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
  # 驗證帳密
  conn = sqlite3.connect("manager.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT 1 FROM manager WHERE account = ? AND pwd = ?",
      (account,pwd)
    )
  result = cursor.fetchone()
  if result is None:
    conn.close()
    return jsonify({"error":"帳號或密碼錯誤"}),400

  session["manager_login"] = account

  return jsonify({"message": "登入成功"})

@bp.get('/logout')
def logout():
  session.clear()
  return redirect(url_for("web.admin.loginPage"))