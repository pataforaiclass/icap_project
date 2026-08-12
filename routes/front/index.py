from flask import Blueprint, render_template
import sqlite3
import os
from bs4 import BeautifulSoup

from routes.front.api import attractions as attr, event, food, member

bp = Blueprint('front', __name__)

bp.register_blueprint(attr.bp, url_prefix="/api/attr")
bp.register_blueprint(event.bp, url_prefix="/api/event")
bp.register_blueprint(food.bp, url_prefix="/api/food")
bp.register_blueprint(member.bp, url_prefix="/api/member")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "database.db")

@bp.get('/api/index')
def get_index_data():
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  # =========================
  # 1. 最新活動
  # =========================
  cursor.execute("""
    SELECT
      event.id,
      event.title,
      event.createTime,
      (
        SELECT event_image.image
        FROM event_image
        WHERE event_image.eventId = event.id
        LIMIT 1
      ) AS image
    FROM event
    ORDER BY event.id DESC
    LIMIT 10
  """)

  event_rows = cursor.fetchall()

  events = []

  for row in event_rows:
    events.append({
      "id": row["id"],
      "title": row["title"],
      "createTime": row["createTime"],
      "image": row["image"]
    })


  # =========================
  # 2. 最新景點
  # =========================
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
    LIMIT 5
  """)

  attraction_rows = cursor.fetchall()

  attractions = []

  for row in attraction_rows:

    # 移除 HTML 標籤
    soup = BeautifulSoup(row["content"] or "", "html.parser")
    content = soup.get_text(strip=True)

    # 取前 20 個字
    content = content[:20]+'...'

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
      "content": content,
      "topics": topics,
      "image": row["image"]
    })


  # =========================
  # 3. 最新美食
  # =========================
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
    content = soup.get_text(strip=True)

    # 取前 20 個字
    content = content[:20]+'...'

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
      "content": content,
      "district": row["district"],
      "topics": topics,
      "image": row["image"]
    })


  conn.close()

  return {
    "events": events,
    "attractions": attractions,
    "foods": foods
  }

# 年度活動
@bp.route("/event/<int:eventId>")
def eventDetailPage(eventId):
  return render_template(
    "front/event_detail.html",
    current_type="event",
    eventId="eventId"
  )

# 熱門景點
@bp.route("/attr/<int:attId>")
def attrDetailPage(attId):
  return render_template(
    "front/attractions_detail.html",
    current_type="attractions",
    attId="attId"
  )

# 美食巡禮
@bp.route("/food/<int:foodId>")
def foodDetailPage(foodId):
  return render_template(
    "front/food_detail.html",
    current_type="food",
    foodId="foodId"
  )