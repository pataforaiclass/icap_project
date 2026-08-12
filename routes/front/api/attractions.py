from flask import Blueprint, request, jsonify
import sqlite3
import os
from bs4 import BeautifulSoup

from utils.datetime import get_tw_time
from utils.auth import api_login_required

bp = Blueprint('attr', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "database.db")

upload_folder = f"static/image/attractions"
thumbnail_folder = f"static/image/attractions/thumbnail"

# 讀取
@bp.get("/")
def get_attr():
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  cursor.execute("""
    SELECT
      attractions.id,
      attractions.title,
      attractions.content,
      (
        SELECT attractions_image.image
        FROM attractions_image
        WHERE attractions_image.attId = attractions.id
        LIMIT 1
      ) AS image
    FROM attractions
    ORDER BY attractions.id DESC
  """)

  rows = cursor.fetchall()

  attractions = []
  
  for row in rows:
  
    # 移除 HTML 標籤
    soup = BeautifulSoup(row["content"] or "", "html.parser")
    contentShort = soup.get_text(strip=True)
  
    # 取前 20 個字
    contentShort = contentShort[:20]+'...'
  
    # 查詢景點主題
    cursor.execute("""
      SELECT name
      FROM attractions_topic
      WHERE attId = ?
    """, (row["id"],))
  
    topic_rows = cursor.fetchall()
  
    topics = [topic["name"] for topic in topic_rows]
  
    attractions.append({
      "id": row["id"],
      "title": row["title"],
      "content": row["content"],
      "contentShort": contentShort,
      "topics": topics,
      "image": row["image"]
    })
    
  conn.close()
  return jsonify({
      "message": "資料讀取成功",
      "attractions": attractions
    }), 200

# 指定 id 讀取
@bp.get("/<int:attId>")
def get_attr_by_id(attId):
  # 連線資料庫
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  # 確認目標是否存在
  cursor.execute("SELECT * FROM attractions WHERE id = ?", (attId,))
  row = cursor.fetchone()
  if row is None:
    conn.close()
    return jsonify({"error": "查無資料"}), 400

  cursor.execute(
      "SELECT name FROM attractions_topic WHERE attId = ?", (attId,))
  topic = []
  topicRows = cursor.fetchall()
  for topicRow in topicRows:
    topic.append(topicRow[0])

  cursor.execute(
      "SELECT image FROM attractions_image WHERE attId = ?", (attId,))
  images = []
  imageRows = cursor.fetchall()
  for imageRow in imageRows:
    images.append(imageRow[0])

  conn.close()
  attr = {
      "id": row[0],
      "title": row[1],
      "content": row[2],
      "postalCode": row[3],
      "city": row[4],
      "district": row[5],
      "address": row[6],
      "tip": row[7],
      "facilities": row[8],
      "topic": topic,
      "images": images,
      "createTime": row[9],
  }
  return jsonify({"message": "資料讀取成功", "attr": attr}), 200

# 新增留言
@bp.post("/comment/")
@api_login_required
def add_comment():
  # 資料格式驗證
  try:
    data = request.get_json(force=False) # 如果出問題，這裡改成 request.form
    if data is None:
      raise ValueError
  except Exception:
    return jsonify({"error":"請傳送正確的json格式資料"}), 400
  # 資料欄位驗證
  required_keys = {"attId","memberId","title","content","evaluate"}
  if not required_keys.issubset(data.keys()):
    return jsonify({"error":"資料提供不全"}), 400
  # 抓取資料
  attId = data.get('attId')
  memberId = data.get('memberId')
  title = data.get('title')
  content = data.get('content')
  evaluate = data.get('evaluate')
  
  # 資料內容驗證
  if not isinstance(attId,int):
    return jsonify({"error":"attId必須是數字"}), 400
  if not isinstance(title,str):
    return jsonify({"error":"名稱必須是文字格式"}), 400
  if not isinstance(content,str):
    return jsonify({"error":"名稱必須是文字格式"}), 400
  if not isinstance(evaluate,int):
    return jsonify({"error":"評分必須是數字"}), 400

  # 連線資料庫
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  dateNow = get_tw_time()

  # 寫入資料
  cursor.execute("""
    INSERT INTO attractions_comment(attId, memberId, title, content, evaluate, createTime)
    VALUES (?, ?, ?, ?, ?, ?)
  """,(attId, memberId, title, content, evaluate, dateNow))
  conn.commit()
  # 抓取最後一筆新增資料的 id
  commentId = cursor.lastrowid

  conn.close()
  
  return jsonify({
    "message":"資料新增成功",
    "data": {
      "id": commentId,
      "attId": attId,
      "memberId": memberId,
      "title": title,
      "content": content,
      "evaluate": evaluate,
      "createTime": dateNow
    }
  }),201