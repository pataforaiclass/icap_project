from flask import Blueprint, request, jsonify
import sqlite3
import re
from utils.datetime import get_tw_time

bp = Blueprint('manager', __name__)

# 建檔，目前只能用 post man 使用
@bp.post('/')
def register_manager():
  # 資料格式驗證
  try:
    data = request.get_json(force=False)
    if data is None:
      raise ValueError
  except Exception:
    return jsonify({"error":"請傳送正確的json格式資料"}), 400
  # 資料欄位驗證
  required_keys = {"account","pwd","userName","email","mobile"}
  if not required_keys.issubset(data.keys()):
    return jsonify({"error":"資料提供不全"}), 400
  # 抓取資料
  account = data.get('account')
  pwd = data.get('pwd')
  userName = data.get('userName')
  email = data.get('email')
  mobile = data.get('mobile')
  # 資料內容驗證
  if not isinstance(account,str) or account.isspace():
    return jsonify({"error":"帳號必須是非純空白文字格式"}), 400
  if not isinstance(pwd,str) or pwd.isspace():
    return jsonify({"error":"密碼必須是非純空白文字格式"}), 400
  pwdPa1 = r'^[^\s]{8,20}$'
  if re.fullmatch(pwdPa1) is None:
    return jsonify({"error":"密碼不符合長度"}), 400
  pwdPa2 = r'^[A-Za-z\d!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?`~]+$'
  if re.fullmatch(pwdPa2) is None:
    return jsonify({"error":"密碼不符合格式"}), 400
  if not isinstance(userName,str) or userName.isspace():
    return jsonify({"error":"用戶名稱必須是非純空白文字格式"}), 400
  if not isinstance(email,str) or email.isspace():
    return jsonify({"error":"電子信箱必須是非純空白文字格式"}), 400
  emailPa = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
  if re.fullmatch(emailPa, email) is None:
    return jsonify({"error":"電子信箱不符合格式"}), 400
  if not isinstance(mobile,str):
    return jsonify({"error":"手機號碼必須是文字格式"}), 400
  mobilePa = r'^(?:09\d{8}|(?:\+?886)9\d{8})$'
  if mobile != "" and re.fullmatch(mobilePa, mobile) is None:
    return jsonify({"error":"手機號碼不符合格式"}), 400

  # 連線資料庫
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  dateNow = get_tw_time()

  # 確認帳號是否重複
  cursor.execute(
    "SELECT 1 FROM manager WHERE account = ?",
    (account,)
  )
  result = cursor.fetchone()
  if result is not None:
    conn.close()
    return jsonify({"error":"此帳號已存在","account":account}),400

  # 寫入資料
  cursor.execute("""
    INSERT INTO manager(account, pwd, userName, email, mobile, createTime)
    VALUES (?, ?, ?, ?, ?, ?)
  """,(
    account, pwd, userName, email, mobile, dateNow
  ))
  conn.commit()
  # 抓取最後一筆新增資料的 id
  userId = cursor.lastrowid
  conn.close()

  return jsonify({
    "message":"帳號資料新增成功",
    "creature": {
      "id": userId,
      "account": account,
      "pwd": "*****",
      "userName": userName,
      "email": email,
      "mobile": mobile,
      "createTime": dateNow
    }
  }),201

