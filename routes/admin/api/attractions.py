from flask import Blueprint, request, jsonify
import sqlite3
import os
import json
from werkzeug.utils import secure_filename

from utils.datetime import get_tw_time
from utils.auth import api_manager_required
from utils.imageUpload import save_image

bp = Blueprint("attr", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "database.db")

upload_folder = os.path.join("static", "image", "attractions")
thumbnail_folder = os.path.join("static", "image", "attractions", "thumbnail")


@bp.post('/')
@api_manager_required
def add_attr():
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
      "postalCode",
      "city",
      "district",
      "address",
      "tip",
      "facilities",
      "topic"
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
  postalCode = data.get("postalCode")
  city = data.get("city")
  district = data.get("district")
  address = data.get("address")
  tip = data.get("tip")
  facilities = data.get("facilities")

  # =========================
  # topic
  # =========================
  try:
    topic = json.loads(data.get("topic"))
  except Exception:
    return jsonify({
        "error": "topic 必須是正確的JSON陣列格式"
    }), 400

  if not isinstance(topic, list):
    return jsonify({
        "error": "topic 必須是陣列格式"
    }), 400

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
      "postalCode": postalCode,
      "city": city,
      "district": district,
      "address": address,
      "tip": tip,
      "facilities": facilities
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
    "postalCode",
    "city",
    "district",
    "address",
    "tip",
    "facilities"
  ]:
    if text_fields[field].isspace():
      return jsonify({
          "error": f"{field} 必須是非純空白文字格式"
      }), 400

  # =========================
  # topic 資料驗證
  # =========================
  for topic_name in topic:
    if not isinstance(topic_name, str):
      return jsonify({
          "error": "分類必須是文字格式"
      }), 400

    if not topic_name.strip():
      return jsonify({
          "error": "分類不可為空白"
      }), 400

  # 移除前後空白
  topic = [
      topic_name.strip()
      for topic_name in topic
  ]

  # 移除重複分類
  topic = list(dict.fromkeys(topic))

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
      INSERT INTO attractions(
        title,
        content,
        postalCode,
        city,
        district,
        address,
        tip,
        facilities,
        createTime
      )
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title.strip(),
        content.strip(),
        postalCode.strip(),
        city.strip(),
        district.strip(),
        address.strip(),
        tip.strip(),
        facilities.strip(),
        date_now
    ))

    # 取得新增景點 ID
    attId = cursor.lastrowid

    # =========================
    # 寫入分類
    # =========================
    for topic_name in topic:
      cursor.execute("""
        INSERT INTO attractions_topic(
          attId,
          name
        )
        VALUES (?, ?)
      """, (
          attId,
          topic_name
      ))

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
        INSERT INTO attractions_image(
          attId,
          image,
          createTime
        )
        VALUES (?, ?, ?)
      """, (
          attId,
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
          "id": attId,
          "title": title.strip(),
          "content": content.strip(),
          "postalCode": postalCode.strip(),
          "city": city.strip(),
          "district": district.strip(),
          "address": address.strip(),
          "tip": tip.strip(),
          "facilities": facilities.strip(),
          "topic": topic,
          "images": img_list,
          "createTime": date_now
      }
  }), 201

# 讀取
@bp.get("/")
@api_manager_required
def get_attr():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  cursor.execute("""
    SELECT
      a.id,
      a.title,
      a.content,
      a.postalCode,
      a.city,
      a.district,
      a.address,
      a.tip,
      a.facilities,
      a.createTime,
      COUNT(DISTINCT ai.image) AS imgCount,
      GROUP_CONCAT(DISTINCT at.name) AS topics
    FROM attractions AS a
    LEFT JOIN attractions_image AS ai
      ON a.id = ai.attId
    LEFT JOIN attractions_topic AS at
      ON a.id = at.attId
    GROUP BY a.id
    ORDER BY a.id DESC
  """)

  rows = cursor.fetchall()
  conn.close()

  attr = []

  for row in rows:
    # GROUP_CONCAT 取得的是字串，例如：
    # "自然景觀,親子景點,戶外活動"
    # 所以這裡再轉回 Python list
    topic = row[11].split(",") if row[11] else []

    item = {
      "id": row[0],
      "title": row[1],
      "content": row[2],
      "postalCode": row[3],
      "city": row[4],
      "district": row[5],
      "address": row[6],
      "tip": row[7],
      "facilities": row[8],
      "createTime": row[9],
      "images": row[10],
      "topic": topic,
      "checked": False
    }

    attr.append(item)

  return jsonify({
    "message": "資料讀取成功",
    "attractions": attr
  }), 200

# 指定 id 讀取
@bp.get("/<int:attId>")
@api_manager_required
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


@bp.patch("/<int:attId>")
@api_manager_required
def patch_attr(attId):
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
        "SELECT * FROM attractions WHERE id = ?",
        (attId,)
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
        "postalCode",
        "city",
        "district",
        "address",
        "tip",
        "facilities"
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
        "postalCode",
        "city",
        "district",
        "address",
        "tip",
        "facilities"
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
    # topic 驗證
    # =========================
    topic_list = None

    if "topic" in data:
      # 因為 multipart/form-data 無法直接傳 Python list
      # 假設前端用 JSON 字串傳送 topic
      import json

      try:
        topic_list = json.loads(data.get("topic"))
      except Exception:
        return jsonify({
            "error": "topic 必須是正確的JSON陣列格式"
        }), 400

      if not isinstance(topic_list, list):
        return jsonify({
            "error": "topic 必須是陣列格式"
        }), 400

      for topic_name in topic_list:
        if not isinstance(topic_name, str) or not topic_name.strip():
          return jsonify({
              "error": "分類必須是非空白文字格式"
          }), 400

      # 去除前後空白
      topic_list = [
          topic_name.strip()
          for topic_name in topic_list
      ]

      # 移除重複 topic
      topic_list = list(dict.fromkeys(topic_list))

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
    if not update_fields and topic_list is None and not images:
      return jsonify({
          "message": "至少提供一個欄位"
      }), 400

    # =========================
    # 更新 attractions
    # =========================
    attr = {
        "id": attId
    }

    if update_fields:
      sql = f"""
        UPDATE attractions
        SET {", ".join(update_fields)}
        WHERE id = ?
      """

      update_values.append(attId)

      cursor.execute(sql, update_values)

      for field, value in zip(
          [field for field in allowed_fields if field in data],
          update_values[:-1]
      ):
        attr[field] = value

    # =========================
    # 更新 topic
    # =========================
    if topic_list is not None:
      # 取得原本 topic
      cursor.execute("""
        SELECT id, name
        FROM attractions_topic
        WHERE attId = ?
      """, (attId,))

      old_topic_rows = cursor.fetchall()

      old_topics = {}

      for topic_row in old_topic_rows:
        topic_id = topic_row[0]
        topic_name = topic_row[1]

        old_topics[topic_name] = topic_id

      # 刪除原本存在，但更新後不存在的 topic
      for old_name, topic_id in old_topics.items():
        if old_name not in topic_list:
          cursor.execute("""
            DELETE FROM attractions_topic
            WHERE id = ?
          """, (topic_id,))

      # 新增原本不存在的 topic
      for topic_name in topic_list:
        if topic_name not in old_topics:
          cursor.execute("""
            INSERT INTO attractions_topic(attId, name)
            VALUES (?, ?)
          """, (
              attId,
              topic_name
          ))

      attr["topic"] = topic_list

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
        INSERT INTO attractions_image(
          attId,
          image,
          createTime
        )
        VALUES (?, ?, ?)
      """, (
          attId,
          image_name,
          get_tw_time()
      ))

      image_list.append(image_name)

    attr["images"] = image_list

    # =========================
    # 寫入資料庫
    # =========================
    conn.commit()

    return jsonify({
        "message": "資料更新成功",
        "attr": attr
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
@bp.delete('/<int:attId>/img/<imgFileName>')
@api_manager_required
def delete_img(attId, imgFileName):
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
    FROM attractions_image
    WHERE attId = ? AND image = ?
    """,
    (attId, imgFileName)
  )

  if cursor.fetchone() is None:
    conn.close()
    return jsonify({
      "error": "找不到指定的圖片"
    }), 404

  # 刪除資料庫中的圖片資料
  cursor.execute(
    """
    DELETE FROM attractions_image
    WHERE attId = ? AND image = ?
    """,
    (attId, imgFileName)
  )

  conn.commit()
  conn.close()

  # 原圖路徑
  image_path = os.path.join(
    "static",
    "image",
    "attractions",
    imgFileName
  )

  # 縮圖路徑
  thumbnail_path = os.path.join(
    "static",
    "image",
    "attractions",
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
    "attId": attId,
    "image": imgFileName
  }), 200

# 刪除
@bp.delete("/<int:attId>")
@api_manager_required
def delete_attr(attId):
  # 連線資料庫
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  try:
    # =========================
    # 確認目標是否存在
    # =========================
    cursor.execute(
        "SELECT * FROM attractions WHERE id = ?",
        (attId,)
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
      FROM attractions_image
      WHERE attId = ?
    """, (attId,))

    image_rows = cursor.fetchall()

    # 將圖片名稱先保存起來
    image_list = []

    for image_row in image_rows:
      image_name = image_row[0]

      if image_name:
        image_list.append(image_name)

    # =========================
    # 刪除資料庫資料
    # =========================

    # 刪除分類
    cursor.execute(
        "DELETE FROM attractions_topic WHERE attId = ?",
        (attId,)
    )

    # 刪除留言
    cursor.execute(
        "DELETE FROM attractions_comment WHERE attId = ?",
        (attId,)
    )

    # 刪除圖片資料
    cursor.execute(
        "DELETE FROM attractions_image WHERE attId = ?",
        (attId,)
    )

    # 刪除景點
    cursor.execute(
        "DELETE FROM attractions WHERE id = ?",
        (attId,)
    )

    # =========================
    # 寫入資料庫
    # =========================
    conn.commit()

  except Exception as e:
    # 發生錯誤時取消所有 DB 操作
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

  return jsonify({
      "message": "資料刪除成功"
  }), 200
