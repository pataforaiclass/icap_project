from flask import Blueprint, request, jsonify
import sqlite3
import os
from utils.datetime import get_tw_time
from utils.auth import api_manager_required
from utils.imageUpload import save_image

bp = Blueprint('event', __name__)

upload_folder = f"static/image/event"
thumbnail_folder = f"static/image/event/thumbnail"

@bp.post('/')
@api_manager_required
def add_event():
  # 資料格式驗證
  try:
    data = request.get_json(force=False)
    if data is None:
      raise ValueError
  except Exception:
    return jsonify({"error":"請傳送正確的json格式資料"}), 400
  # 資料欄位驗證
  required_keys = {"title","content","organizer","postalCode","city","district","address","image"}
  if not required_keys.issubset(data.keys()):
    return jsonify({"error":"資料提供不全"}), 400
  # 抓取資料
  title = data.get('title')
  content = data.get('content')
  organizer = data.get('organizer')
  postalCode = data.get('postalCode')
  city = data.get('city')
  district = data.get('district')
  address = data.get('address')
  images = data.getlist('image')
  # 資料內容驗證
  if not isinstance(title,str) or title.isspace():
    return jsonify({"error":"標題必須是非純空白文字格式"}), 400
  if not isinstance(content,str) or content.isspace():
    return jsonify({"error":"內容必須是非純空白文字格式"}), 400
  if not isinstance(organizer,str):
    return jsonify({"error":"主辦單位必須是文字格式"}), 400
  if not isinstance(postalCode,str):
    return jsonify({"error":"郵遞區號必須是文字格式"}), 400
  if not isinstance(city,str):
    return jsonify({"error":"城市必須是文字格式"}), 400
  if not isinstance(district,str):
    return jsonify({"error":"地區必須是文字格式"}), 400
  if not isinstance(address,str):
    return jsonify({"error":"住址必須是文字格式"}), 400

  # 連線資料庫
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  dateNow = get_tw_time()

  # 寫入資料
  cursor.execute("""
    INSERT INTO event(title, content, organizer, postalCode, city, district, address, createTime)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  """,(
    title, content, organizer, postalCode, city, district, address, dateNow
  ))
  conn.commit()
  # 抓取最後一筆新增資料的 id
  eventId = cursor.lastrowid

  # 處理圖檔
  imgList = []
  for img in images:
    imgName = save_image(img, upload_folder, thumbnail_folder)
    imgList.append(imgName)
    if images is not None:
      cursor.execute("""
        INSERT INTO event_image(eventId, image, createTime)
        VALUES (?, ?, ?)
      """,(eventId, imgName, get_tw_time()))
      conn.commit()
  
  conn.close()

  return jsonify({
    "message":"資料新增成功",
    "creature": {
      "id": eventId,
      "title": title,
      "content": content,
      "organizer": organizer,
      "postalCode": postalCode,
      "city": city,
      "district": district,
      "address": address,
      "images": imgList,
      "createTime": dateNow
    }
  }),201

# 讀取
@bp.get('/')
@api_manager_required
def get_event():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM event")
  rows = cursor.fetchall()
  conn.close()
  event = []
  for row in rows:
    cursor.execute("SELECT image FROM event_image WHERE eventId = ?",(row[0],))
    images = []
    imageRows = cursor.fetchall()
    for imageRow in imageRows:
      images.append(imageRow[0])

    item = {
      "id": row[0],
      "title": row[1],
      "content": row[2],
      "organizer": row[3],
      "postalCode": row[4],
      "city": row[5],
      "district": row[6],
      "address": row[7],
      "images": images,
      "createTime": row[8]
    }
    event.append(item)

  return jsonify({"message":"資料讀取成功","event":event}),200

# 指定 id 讀取
@bp.get('/<int:eventId>')
@api_manager_required
def get_event_by_id(eventId):
  # 連線資料庫
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  
  # 確認目標是否存在
  cursor.execute("SELECT * FROM event WHERE id = ?",(eventId,))
  row = cursor.fetchone()
  if row is None:
    conn.close()
    return jsonify({"error":"查無資料"}),400

  cursor.execute("SELECT image FROM event_image WHERE eventId = ?",(row[0],))
  images = []
  imageRows = cursor.fetchall()
  for imageRow in imageRows:
    images.append(imageRow[0])

  conn.close()
  event = {
    "id": row[0],
    "title": row[1],
    "content": row[2],
    "organizer": row[3],
    "postalCode": row[4],
    "city": row[5],
    "district": row[6],
    "address": row[7],
    "images": images,
    "createTime": row[8]
  }
  return jsonify({"message":"資料讀取成功","event":event}),200

@bp.patch('/<int:eventId>')
@api_manager_required
def patch_event(eventId): # 修改圖片部分還沒做
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
  cursor.execute("SELECT * FROM event WHERE id = ?",(eventId,))
  row = cursor.fetchone()
  if row is None:
    conn.close()
    return jsonify({"error":"查無資料"}),400

  event = {}
  sql = "UPDATE event SET"
  patched = False # 若有欄位更新為 True

  if "title" in data:
    title = data.get('title')
    if isinstance(title,str) and not title.isspace():
      event['title'] = title
      sql += " title = ?"
      patched = True

  if "content" in data:
    content = data.get('content')
    if isinstance(content,str) and not content.isspace():
      event['content'] = content
      if patched:
        sql += ","
      sql += " content = ?"
      patched = True

  if "organizer" in data:
    organizer = data.get('organizer')
    if isinstance(organizer,str) and not organizer.isspace():
      event['organizer'] = organizer
      if patched:
        sql += ","
      sql += " organizer = ?"
      patched = True

  if "postalCode" in data:
    postalCode = data.get('postalCode')
    if isinstance(postalCode,str) and not postalCode.isspace():
      event['postalCode'] = postalCode
      if patched:
        sql += ","
      sql += " postalCode = ?"
      patched = True

  if "city" in data:
    city = data.get('city')
    if isinstance(city,str) and not city.isspace():
      event['city'] = city
      if patched:
        sql += ","
      sql += " city = ?"
      patched = True

  if "district" in data:
    district = data.get('district')
    if isinstance(district,str) and not district.isspace():
      event['district'] = district
      if patched:
        sql += ","
      sql += " district = ?"
      patched = True

  if "address" in data:
    address = data.get('address')
    if isinstance(address,str) and not address.isspace():
      event['address'] = address
      if patched:
        sql += ","
      sql += " address = ?"
      patched = True
  
  if not patched:
    conn.close()
    return jsonify({"message":"至少提供一個欄位"}),400

  event['id'] = eventId
  cursor.execute(sql+" WHERE id = ?",tuple(event.values()))
  conn.commit()

  conn.close()
  return jsonify({"message":"資料更新成功","event":event}),200

# 刪除
@bp.delete('/<int:eventId>')
@api_manager_required
def delete_event(eventId):
  # 連線資料庫
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()

  # 確認目標是否存在
  cursor.execute("SELECT * FROM event WHERE id = ?",(eventId,))
  row = cursor.fetchone()
  if row is None:
    conn.close()
    return jsonify({"error":"查無資料"}),400

  # 執行刪除
  cursor.execute("DELETE FROM event WHERE id = ?",(eventId,))
  conn.commit()
  cursor.execute("DELETE FROM event_image WHERE eventId = ?",(eventId,))
  conn.commit()
  
  conn.close()
  return jsonify({"message":"資料刪除成功"}),200