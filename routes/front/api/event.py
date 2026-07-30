from flask import Blueprint, request, jsonify
import sqlite3
import os
from utils.datetime import get_tw_time
from utils.auth import api_login_required

bp = Blueprint('event', __name__)

upload_folder = f"static/image/event"
thumbnail_folder = f"static/image/event/thumbnail"

# 讀取
@bp.get('/')
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