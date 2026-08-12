from flask import Blueprint, request, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename

from utils.datetime import get_tw_time
from utils.auth import api_manager_required
from utils.imageUpload import save_image

bp = Blueprint('event', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "database.db")

upload_folder = os.path.join(
    "static",
    "image",
    "event"
)
thumbnail_folder = os.path.join(
    "static",
    "image",
    "event",
    "thumbnail"
)


@bp.post('/')
@api_manager_required
def add_event():
  # =========================
  # 取得表單資料
  # =========================
  data = request.form

  # =========================
  # 必要欄位
  # =========================
  required_fields = {
      "title",
      "content",
      "organizer",
      "postalCode",
      "city",
      "district",
      "address"
  }

  missing_fields = [
      field
      for field in required_fields
      if field not in data
  ]

  if missing_fields:
    return jsonify({
        "error": "資料提供不全",
        "missing": missing_fields
    }), 400

  # =========================
  # 取得資料
  # =========================
  title = data.get("title")
  content = data.get("content")
  organizer = data.get("organizer")
  postalCode = data.get("postalCode")
  city = data.get("city")
  district = data.get("district")
  address = data.get("address")

  # =========================
  # 圖片
  # =========================
  images = request.files.getlist("image")

  # =========================
  # 文字資料驗證
  # =========================
  text_fields = {
      "title": title,
      "content": content,
      "organizer": organizer,
      "postalCode": postalCode,
      "city": city,
      "district": district,
      "address": address
  }

  for field, value in text_fields.items():
    if not isinstance(value, str):
      return jsonify({
          "error": f"{field} 必須是文字格式"
      }), 400

  # title / content 不允許空白
  if not title.strip():
    return jsonify({
        "error": "名稱必須是非純空白文字格式"
    }), 400

  if not content.strip():
    return jsonify({
        "error": "內容必須是非純空白文字格式"
    }), 400

  # 其餘欄位也不允許純空白
  for field in [
    "organizer",
    "postalCode",
    "city",
    "district",
    "address"
  ]:
    if text_fields[field].isspace():
      return jsonify({
          "error": f"{field} 必須是非純空白文字格式"
      }), 400

  # =========================
  # 圖片資料驗證
  # =========================
  images = [
      image
      for image in images
      if image and image.filename
  ]

  # =========================
  # 連線資料庫
  # =========================
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  # 用來記錄已經成功儲存的圖片
  # 如果 DB 發生錯誤，可以刪除這些檔案
  saved_images = []

  try:
    # =========================
    # 建立景點資料
    # =========================
    date_now = get_tw_time()

    cursor.execute("""
      INSERT INTO event(
        title,
        content,
        organizer,
        postalCode,
        city,
        district,
        address,
        createTime
      )
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title.strip(),
        content.strip(),
        organizer.strip(),
        postalCode.strip(),
        city.strip(),
        district.strip(),
        address.strip(),
        date_now
    ))

    # 取得新增景點 ID
    eventId = cursor.lastrowid

    # =========================
    # 處理圖檔
    # =========================
    img_list = []

    for image in images:
      image_name = save_image(
          image,
          upload_folder,
          thumbnail_folder
      )

      # 圖片儲存失敗
      if image_name is None:
        continue

      img_list.append(image_name)
      saved_images.append(image_name)

      cursor.execute("""
        INSERT INTO event_image(
          eventId,
          image,
          createTime
        )
        VALUES (?, ?, ?)
      """, (
          eventId,
          image_name,
          get_tw_time()
      ))

    # =========================
    # 寫入資料庫
    # =========================
    conn.commit()

  except Exception as e:
    # =========================
    # DB rollback
    # =========================
    conn.rollback()

    # =========================
    # 刪除已經成功儲存的圖片
    # =========================
    for image_name in saved_images:
      image_path = os.path.join(
          upload_folder,
          image_name
      )

      thumbnail_path = os.path.join(
          thumbnail_folder,
          image_name
      )

      if os.path.isfile(image_path):
        os.remove(image_path)

      if os.path.isfile(thumbnail_path):
        os.remove(thumbnail_path)

    return jsonify({
        "error": "資料新增失敗",
        "detail": str(e)
    }), 500

  finally:
    conn.close()

  # =========================
  # 回傳資料
  # =========================
  return jsonify({
      "message": "資料新增成功",
      "data": {
          "id": eventId,
          "title": title.strip(),
          "content": content.strip(),
          "organizer": organizer.strip(),
          "postalCode": postalCode.strip(),
          "city": city.strip(),
          "district": district.strip(),
          "address": address.strip(),
          "images": img_list,
          "createTime": date_now
      }
  }), 201

# 讀取
@bp.get('/')
@api_manager_required
def get_event():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  cursor.execute("""
    SELECT
      e.id,
      e.title,
      e.content,
      e.organizer,
      e.postalCode,
      e.city,
      e.district,
      e.address,
      e.createTime,
      COUNT(ei.eventId) AS imgCount
    FROM event AS e
    LEFT JOIN event_image AS ei
      ON e.id = ei.eventId
    GROUP BY e.id
    ORDER BY e.id DESC
  """)

  rows = cursor.fetchall()
  conn.close()

  event = []

  for row in rows:
    item = {
      "id": row[0],
      "title": row[1],
      "content": row[2],
      "organizer": row[3],
      "postalCode": row[4],
      "city": row[5],
      "district": row[6],
      "address": row[7],
      "createTime": row[8],
      "images": row[9],
      "checked": False
    }

    event.append(item)

  return jsonify({
    "message": "資料讀取成功",
    "event": event
  }), 200

# 指定 id 讀取
@bp.get('/<int:eventId>')
@api_manager_required
def get_event_by_id(eventId):
  # 連線資料庫
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  # 確認目標是否存在
  cursor.execute("SELECT * FROM event WHERE id = ?", (eventId,))
  row = cursor.fetchone()
  if row is None:
    conn.close()
    return jsonify({"error": "查無資料"}), 400

  cursor.execute("SELECT image FROM event_image WHERE eventId = ?", (row[0],))
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
  return jsonify({"message": "資料讀取成功", "event": event}), 200


@bp.patch('/<int:eventId>')
@api_manager_required
def patch_event(eventId):
  # =========================
  # 資料格式驗證
  # =========================
  data = request.form

  # =========================
  # 連線資料庫
  # =========================
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  try:
    # =========================
    # 確認目標是否存在
    # =========================
    cursor.execute(
        "SELECT * FROM event WHERE id = ?",
        (eventId,)
    )

    row = cursor.fetchone()

    if row is None:
      return jsonify({
          "error": "查無資料"
      }), 400

    # =========================
    # 要更新的景點欄位
    # =========================
    allowed_fields = [
        "title",
        "content",
        "organizer",
        "postalCode",
        "city",
        "district",
        "address"
    ]

    update_fields = []
    update_values = []

    # =========================
    # 景點資料驗證
    # =========================
    for field in allowed_fields:
      if field not in data:
        continue

      value = data.get(field)
      canNullField = [
        "organizer",
        "postalCode",
        "city",
        "district",
        "address"
      ]

      if field not in canNullField and (not isinstance(value, str) or not value.strip()):
        return jsonify({
            "error": f"{field} 必須是非空白文字格式"
        }), 400

      if field in canNullField and (not isinstance(value, str)):
        return jsonify({
            "error": f"{field} 必須是文字格式"
        }), 400

      update_fields.append(f"{field} = ?")
      update_values.append(value.strip())

    # =========================
    # 圖片
    # =========================
    images = request.files.getlist("image")

    # 移除沒有檔案的項目
    images = [
        image
        for image in images
        if image and image.filename
    ]

    # =========================
    # 確認是否至少有一項修改
    # =========================
    if not update_fields and not images:
      return jsonify({
          "message": "至少提供一個欄位"
      }), 400

    # =========================
    # 更新 event
    # =========================
    event = {
        "id": eventId
    }

    if update_fields:
      sql = f"""
        UPDATE event
        SET {", ".join(update_fields)}
        WHERE id = ?
      """

      update_values.append(eventId)

      cursor.execute(sql, update_values)

      for field, value in zip(
          [field for field in allowed_fields if field in data],
          update_values[:-1]
      ):
        event[field] = value

    # =========================
    # 上傳圖檔
    # =========================
    image_list = []

    for image in images:
      image_name = save_image(
          image,
          upload_folder,
          thumbnail_folder
      )

      if image_name is None:
        continue

      cursor.execute("""
        INSERT INTO event_image(
          eventId,
          image,
          createTime
        )
        VALUES (?, ?, ?)
      """, (
          eventId,
          image_name,
          get_tw_time()
      ))

      image_list.append(image_name)

    event["images"] = image_list

    # =========================
    # 寫入資料庫
    # =========================
    conn.commit()

    return jsonify({
        "message": "資料更新成功",
        "event": event
    }), 200

  except Exception as e:
    conn.rollback()

    return jsonify({
        "error": "資料更新失敗",
        "detail": str(e)
    }), 500

  finally:
    conn.close()

# 刪除單個圖片
@bp.delete('/<int:eventId>/img/<imgFileName>')
@api_manager_required
def delete_img(eventId, imgFileName):
  # =========================
  # 檔名安全性檢查
  # =========================

  safe_filename = secure_filename(imgFileName)
  # 如果檔名經過清理後與原本不同
  # 代表可能包含不允許的字元或路徑
  if safe_filename != imgFileName or not safe_filename:
    return jsonify({
      "error": "無效的圖片檔名"
    }), 400

  allowed_extensions = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
  }

  ext = os.path.splitext(imgFileName)[1].lower()

  if ext not in allowed_extensions:
    return jsonify({
      "error": "不支援的圖片格式"
    }), 400

  # =========================
  # 資料庫
  # =========================
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  # 先確認圖片資料是否存在
  cursor.execute(
    """
    SELECT 1
    FROM event_image
    WHERE eventId = ? AND image = ?
    """,
    (eventId, imgFileName)
  )

  if cursor.fetchone() is None:
    conn.close()
    return jsonify({
      "error": "找不到指定的圖片"
    }), 404

  # 刪除資料庫中的圖片資料
  cursor.execute(
    """
    DELETE FROM event_image
    WHERE eventId = ? AND image = ?
    """,
    (eventId, imgFileName)
  )

  conn.commit()
  conn.close()

  # 原圖路徑
  image_path = os.path.join(
    "static",
    "image",
    "event",
    imgFileName
  )

  # 縮圖路徑
  thumbnail_path = os.path.join(
    "static",
    "image",
    "event",
    "thumbnail",
    imgFileName
  )

  # 刪除原圖
  if os.path.exists(image_path):
    os.remove(image_path)

  # 刪除縮圖
  if os.path.exists(thumbnail_path):
    os.remove(thumbnail_path)

  return jsonify({
    "message": "圖片刪除成功",
    "eventId": eventId,
    "image": imgFileName
  }), 200

# 刪除
@bp.delete('/<int:eventId>')
@api_manager_required
def delete_event(eventId):
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  image_list = []

  try:
    # =========================
    # 確認目標是否存在
    # =========================
    cursor.execute(
      "SELECT * FROM event WHERE id = ?",
      (eventId,)
    )

    row = cursor.fetchone()

    if row is None:
      return jsonify({
        "error": "查無資料"
      }), 400

    # =========================
    # 取得圖片資料
    # =========================
    cursor.execute("""
      SELECT image
      FROM event_image
      WHERE eventId = ?
    """, (eventId,))

    image_rows = cursor.fetchall()

    for image_row in image_rows:
      image_name = image_row[0]

      if image_name:
        image_list.append(image_name)

    # =========================
    # 刪除資料庫資料
    # =========================

    # 刪除圖片資料
    cursor.execute(
      "DELETE FROM event_image WHERE eventId = ?",
      (eventId,)
    )

    # 刪除活動
    cursor.execute(
      "DELETE FROM event WHERE id = ?",
      (eventId,)
    )

    # =========================
    # 寫入資料庫
    # =========================
    conn.commit()

  except Exception as e:
    conn.rollback()

    return jsonify({
      "error": "資料刪除失敗",
      "detail": str(e)
    }), 500

  finally:
    conn.close()

  # =========================
  # 刪除實體圖片
  # =========================
  try:
    for image_name in image_list:

      # 原圖
      image_path = os.path.join(
        upload_folder,
        image_name
      )

      # 縮圖
      thumbnail_path = os.path.join(
        thumbnail_folder,
        image_name
      )

      # 刪除原圖
      if os.path.isfile(image_path):
        os.remove(image_path)

      # 刪除縮圖
      if os.path.isfile(thumbnail_path):
        os.remove(thumbnail_path)

  except Exception as e:
    return jsonify({
      "error": "資料已刪除，但圖片檔案刪除失敗",
      "detail": str(e)
    }), 500

  return jsonify({
    "message": "資料刪除成功"
  }), 200
