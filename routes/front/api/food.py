from flask import Blueprint, request, jsonify
import sqlite3
import os
from bs4 import BeautifulSoup

from utils.datetime import get_tw_time
from utils.auth import api_login_required

bp = Blueprint('food', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "database.db")

upload_folder = f"static/image/food"
thumbnail_folder = f"static/image/food/thumbnail"

# 讀取
@bp.get('/')
def get_food():
  conn = sqlite3.connect("database/database.db")
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  cursor.execute("""
    SELECT
      food.id,
      food.title,
      food.content,
      food.district,
      (
        SELECT food_image.image
        FROM food_image
        WHERE food_image.foodId = food.id
        LIMIT 1
      ) AS image
    FROM food
    ORDER BY food.id DESC
    LIMIT 6
  """)
  
  food_rows = cursor.fetchall()
  
  foods = []
  
  for row in food_rows:
  
    # 移除 HTML 標籤
    soup = BeautifulSoup(row["content"] or "", "html.parser")
    contentShort = soup.get_text(strip=True)
  
    # 取前 20 個字
    contentShort = contentShort[:20]+'...'
  
    # 查詢美食主題
    cursor.execute("""
      SELECT name
      FROM food_topic
      WHERE foodId = ?
    """, (row["id"],))
  
    topic_rows = cursor.fetchall()
  
    topics = [topic["name"] for topic in topic_rows]
  
    foods.append({
      "id": row["id"],
      "title": row["title"],
      "content": row["content"],
      "contentShort": contentShort,
      "district": row["district"],
      "topics": topics,
      "image": row["image"]
    })
  
  
  conn.close()

  return jsonify({
    "message": "資料讀取成功",
    "food": foods
  }), 200

# 指定 id 讀取
@bp.get('/<int:foodId>')
def get_food_by_id(foodId):
  # 連線資料庫
  conn = sqlite3.connect("database/database.db")
  cursor = conn.cursor()

  # 確認目標是否存在
  cursor.execute("SELECT * FROM food WHERE id = ?", (foodId,))
  row = cursor.fetchone()
  if row is None:
    conn.close()
    return jsonify({"error": "查無資料"}), 400

  cursor.execute("SELECT name FROM food_topic WHERE foodId = ?", (foodId,))
  topic = []
  topicRows = cursor.fetchall()
  for topicRow in topicRows:
    topic.append(topicRow[0])

  cursor.execute("SELECT image FROM food_image WHERE foodId = ?", (foodId,))
  images = []
  imageRows = cursor.fetchall()
  for imageRow in imageRows:
    images.append(imageRow[0])

  conn.close()
  food = {
    "id": row[0],
    "title": row[1],
    "content": row[2],
    "postalCode": row[3],
    "city": row[4],
    "district": row[5],
    "address": row[6],
    "phone1": row[7],
    "phone2": row[8],
    "facilities": row[9],
    "topic": topic,
    "images": images,
    "createTime": row[10]
  }
  return jsonify({"message": "資料讀取成功", "food": food}), 200

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
  required_keys = {"foodId","memberId","title","content","evaluate"}
  if not required_keys.issubset(data.keys()):
    return jsonify({"error":"資料提供不全"}), 400
  # 抓取資料
  foodId = data.get('foodId')
  memberId = data.get('memberId')
  title = data.get('title')
  content = data.get('content')
  evaluate = data.get('evaluate')
  
  # 資料內容驗證
  if not isinstance(foodId,int):
    return jsonify({"error":"foodId必須是數字"}), 400
  if not isinstance(title,str):
    return jsonify({"error":"名稱必須是文字格式"}), 400
  if not isinstance(content,str):
    return jsonify({"error":"名稱必須是文字格式"}), 400
  if not isinstance(evaluate,int):
    return jsonify({"error":"評分必須是數字"}), 400

  # 連線資料庫
  conn = sqlite3.connect("database/database.db")
  cursor = conn.cursor()
  dateNow = get_tw_time()

  # 寫入資料
  cursor.execute("""
    INSERT INTO food_comment(foodId, memberId, title, content, evaluate, createTime)
    VALUES (?, ?, ?, ?, ?, ?)
  """,(foodId, memberId, title, content, evaluate, dateNow))
  conn.commit()
  # 抓取最後一筆新增資料的 id
  commentId = cursor.lastrowid

  conn.close()
  
  return jsonify({
    "message":"資料新增成功",
    "data": {
      "id": commentId,
      "foodId": foodId,
      "memberId": memberId,
      "title": title,
      "content": content,
      "evaluate": evaluate,
      "createTime": dateNow
    }
  }),201