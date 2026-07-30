from flask import Blueprint, request, jsonify
import sqlite3
import os
from utils.datetime import get_tw_time
from utils.auth import api_manager_required
from utils.imageUpload import save_image

bp = Blueprint('food', __name__)

upload_folder = f"static/image/food"
thumbnail_folder = f"static/image/food/thumbnail"

@bp.post('/')
@api_manager_required
def add_food():
  # 資料格式驗證
  try:
    data = request.get_json(force=False) # 如果出問題，這裡改成 request.form
    if data is None:
      raise ValueError
  except Exception:
    return jsonify({"error":"請傳送正確的json格式資料"}), 400
  # 資料欄位驗證
  required_keys = {"name","content","postalCode","city","district","address","phone1","phone2","facilities","topic","image"}
  if not required_keys.issubset(data.keys()):
    return jsonify({"error":"資料提供不全"}), 400
  # 抓取資料
  name = data.get('name')
  content = data.get('content')
  postalCode = data.get('postalCode')
  city = data.get('city')
  district = data.get('district')
  address = data.get('address')
  phone1 = data.get('phone1')
  phone2 = data.get('phone2')
  facilities = data.get('facilities')
  topic = data.getlist('topic')
  images = data.getlist('image')

  # 資料內容驗證
  if not isinstance(name,str) or name.isspace():
    return jsonify({"error":"名稱必須是非純空白文字格式"}), 400
  if not isinstance(content,str) or content.isspace():
    return jsonify({"error":"內容必須是非純空白文字格式"}), 400
  if not isinstance(postalCode,str):
    return jsonify({"error":"郵遞區號必須是文字格式"}), 400
  if not isinstance(city,str):
    return jsonify({"error":"城市必須是文字格式"}), 400
  if not isinstance(district,str):
    return jsonify({"error":"地區必須是文字格式"}), 400
  if not isinstance(address,str):
    return jsonify({"error":"住址必須是文字格式"}), 400
  if not isinstance(phone1,str):
    return jsonify({"error":"電話01必須是文字格式"}), 400
  if not isinstance(phone2,str):
    return jsonify({"error":"電話02必須是文字格式"}), 400
  if not isinstance(facilities,str):
    return jsonify({"error":"服務設施必須是文字格式"}), 400
  for topicItem in topic:
    if not isinstance(topicItem,str):
      return jsonify({"error":"分類必須是文字格式"}), 400

  # 連線資料庫
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  dateNow = get_tw_time()

  # 寫入資料
  cursor.execute("""
    INSERT INTO food(name, content, postalCode, city, district, address, phone1, phone2, facilities, createTime)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  """,(
    name, content, postalCode, city, district, address, phone1, phone2, facilities, dateNow
  ))
  conn.commit()
  # 抓取最後一筆新增資料的 id
  foodId = cursor.lastrowid
  # 寫入分類資料
  for topicItem in topic:
    cursor.execute("""
      INSERT INTO food_topic(foodId, name)
      VALUES (?, ?)
    """,(foodId, topicItem))
    conn.commit()
  
  # 處理圖檔
  imgList = []
  for img in images:
    imgName = save_image(img, upload_folder, thumbnail_folder)
    imgList.append(imgName)
    if images is not None:
      cursor.execute("""
        INSERT INTO food_image(foodId, image, createTime)
        VALUES (?, ?, ?)
      """,(foodId, imgName, get_tw_time()))
      conn.commit()

  conn.close()

  return jsonify({
    "message":"資料新增成功",
    "creature": {
      "id": foodId,
      "name": name,
      "content": content,
      "postalCode": postalCode,
      "city": city,
      "district": district,
      "address": address,
      "phone1": phone1,
      "facilities": facilities,
      "topic": topic,
      "images": imgList,
      "createTime": dateNow
    }
  }),201

# 讀取
@bp.get('/')
@api_manager_required
def get_food():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM food")
  rows = cursor.fetchall()
  conn.close()
  food = []
  for row in rows:
    cursor.execute("SELECT name FROM food_topic WHERE foodId = ?",(row[0],))
    topic = []
    topicRows = cursor.fetchall()
    for topicRow in topicRows:
      topic.append(topicRow[0])

    cursor.execute("SELECT image FROM food_image WHERE foodId = ?",(row[0],))
    images = []
    imageRows = cursor.fetchall()
    for imageRow in imageRows:
      images.append(imageRow[0])
    
    item = {
      "id": row[0],
      "title": row[1],
      "content": row[2],
      "postalCode": row[3],
      "city": row[4],
      "district": row[5],
      "address": row[6],
      "phone1": row[7],
      "facilities": row[8],
      "topic": topic,
      "images": images,
      "createTime": row[9]
    }
    food.append(item)
  return jsonify({"message":"資料讀取成功","food":food}),200

# 指定 id 讀取
@bp.get('/<int:foodId>')
@api_manager_required
def get_food_by_id(foodId):
  # 連線資料庫
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  
  # 確認目標是否存在
  cursor.execute("SELECT * FROM food WHERE id = ?",(foodId,))
  row = cursor.fetchone()
  if row is None:
    conn.close()
    return jsonify({"error":"查無資料"}),400

  cursor.execute("SELECT name FROM food_topic WHERE foodId = ?",(foodId,))
  topic = []
  topicRows = cursor.fetchall()
  for topicRow in topicRows:
    topic.append(topicRow[0])

  cursor.execute("SELECT image FROM food_image WHERE foodId = ?",(foodId,))
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
  return jsonify({"message":"資料讀取成功","food":food}),200

@bp.patch('/<int:foodId>')
@api_manager_required
def patch_food(foodId): # 修改圖片部分還沒做
  # 資料格式驗證
  try:
    data = request.get_json(force=False)
    if data is None:
      raise ValueError
  except Exception:
    return jsonify({"error":"請傳送正確的json格式資料"}), 400
  # 連線資料庫
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()

  # 確認目標是否存在
  cursor.execute("SELECT * FROM food WHERE id = ?",(foodId,))
  row = cursor.fetchone()
  if row is None:
    conn.close()
    return jsonify({"error":"查無資料"}),400

  food = {}
  sql = "UPDATE food SET"
  patched = False # 若有欄位更新為 True

  if "title" in data:
    title = data.get('title')
    if isinstance(title,str) and not title.isspace():
      food['title'] = title
      sql += " title = ?"
      patched = True

  if "content" in data:
    content = data.get('content')
    if isinstance(content,str) and not content.isspace():
      food['content'] = content
      if patched:
        sql += ","
      sql += " content = ?"
      patched = True

  if "postalCode" in data:
    postalCode = data.get('postalCode')
    if isinstance(postalCode,str) and not postalCode.isspace():
      food['postalCode'] = postalCode
      if patched:
        sql += ","
      sql += " postalCode = ?"
      patched = True

  if "city" in data:
    city = data.get('city')
    if isinstance(city,str) and not city.isspace():
      food['city'] = city
      if patched:
        sql += ","
      sql += " city = ?"
      patched = True

  if "district" in data:
    district = data.get('district')
    if isinstance(district,str) and not district.isspace():
      food['district'] = district
      if patched:
        sql += ","
      sql += " district = ?"
      patched = True

  if "address" in data:
    address = data.get('address')
    if isinstance(address,str) and not address.isspace():
      food['address'] = address
      if patched:
        sql += ","
      sql += " address = ?"
      patched = True

  if "phone1" in data:
    phone1 = data.get('phone1')
    if isinstance(phone1,str) and not phone1.isspace():
      food['phone1'] = phone1
      if patched:
        sql += ","
      sql += " phone1 = ?"
      patched = True

  if "phone2" in data:
    phone2 = data.get('phone2')
    if isinstance(phone2,str) and not phone2.isspace():
      food['phone2'] = phone2
      if patched:
        sql += ","
      sql += " phone2 = ?"
      patched = True

  if "facilities" in data:
    facilities = data.get('facilities')
    if isinstance(facilities,str) and not facilities.isspace():
      food['facilities'] = facilities
      if patched:
        sql += ","
      sql += " facilities = ?"
      patched = True

  if "topic" in data:
    topic = data.getlist('topic')
    topicList = []
    for topicName in topic:
      if isinstance(topicName,str) and not topicName.isspace():
        topicList.append(topicName)
    cursor.execute("SELECT name FROM food_topic WHERE foodId = ?",(foodId,))
    topicRows = cursor.fetchall()
    for topicRow in topicRows:
      pass
  
  if not patched:
    conn.close()
    return jsonify({"message":"至少提供一個欄位"}),400

  food['id'] = foodId
  cursor.execute(sql+" WHERE id = ?",tuple(food.values()))
  conn.commit()

  conn.close()
  return jsonify({"message":"資料更新成功","food":food}),200

# 刪除
@bp.delete('/<int:foodId>')
@api_manager_required
def delete_food(foodId):
  # 連線資料庫
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()

  # 確認目標是否存在
  cursor.execute("SELECT * FROM food WHERE id = ?",(foodId,))
  row = cursor.fetchone()
  if row is None:
    conn.close()
    return jsonify({"error":"查無資料"}),400

  # 執行刪除
  cursor.execute("DELETE FROM food WHERE id = ?",(foodId,))
  conn.commit()
  cursor.execute("DELETE FROM food_topic WHERE foodId = ?",(foodId,))
  conn.commit()
  cursor.execute("DELETE FROM food_comment WHERE foodId = ?",(foodId,))
  conn.commit()
  cursor.execute("DELETE FROM food_image WHERE foodId = ?",(foodId,))
  conn.commit()
  
  conn.close()
  return jsonify({"message":"資料刪除成功"}),200