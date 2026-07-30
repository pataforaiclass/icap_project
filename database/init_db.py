import sqlite3

# 啟動時如果尚未存在資料庫&資料表便自動建立
def init_db():
  conn = sqlite3.connect("database/database.db")
  cursor = conn.cursor()
  initTableStr = ""

  cursor.execute("""
    SELECT COUNT(*)
    FROM sqlite_master
    WHERE type='table' AND name='manager'
  """)
  if not cursor.fetchone()[0] > 0:
    initTableStr += "manager"
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS manager (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account TEXT NOT NULL UNIQUE,
        pwd TEXT NOT NULL,
        userName TEXT NOT NULL,
        email TEXT NOT NULL,
        mobile TEXT,
        createTime DATE NOT NULL
      )
    ''')
    conn.commit()
  
  cursor.execute("""
    SELECT COUNT(*)
    FROM sqlite_master
    WHERE type='table' AND name='member'
  """)
  if not cursor.fetchone()[0] > 0:
    if initTableStr:
      initTableStr += ","
    initTableStr += "member"
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS member (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account TEXT NOT NULL UNIQUE,
        pwd TEXT NOT NULL,
        userName TEXT NOT NULL,
        gender TEXT,
        birthday DATE,
        email TEXT NOT NULL,
        mobile TEXT,
        createTime DATE NOT NULL
      )
    ''')
    conn.commit()
  
  cursor.execute("""
    SELECT COUNT(*)
    FROM sqlite_master
    WHERE type='table' AND name='event'
  """)
  if not cursor.fetchone()[0] > 0:
    if initTableStr:
      initTableStr += ","
    initTableStr += "event"
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS event (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        organizer TEXT,
        postalCode TEXT,
        city TEXT,
        district TEXT,
        address TEXT,
        createTime DATE NOT NULL
      )
    ''')
    conn.commit()

  cursor.execute("""
      SELECT COUNT(*)
      FROM sqlite_master
      WHERE type='table' AND name='event_image'
    """)
  if not cursor.fetchone()[0] > 0:
    if initTableStr:
      initTableStr += ","
    initTableStr += "event_image"
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS event_image (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eventId INTEGER NOT NULL,
        image TEXT NOT NULL,
        createTime DATE NOT NULL
      )
    ''')
    conn.commit()
  
  cursor.execute("""
    SELECT COUNT(*)
    FROM sqlite_master
    WHERE type='table' AND name='attractions'
  """)
  if not cursor.fetchone()[0] > 0:
    if initTableStr:
      initTableStr += ","
    initTableStr += "attractions"
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS attractions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        content TEXT NOT NULL,
        postalCode TEXT,
        city TEXT,
        cidistrictty TEXT,
        address TEXT,
        tip TEXT,
        facilities TEXT,
        createTime DATE NOT NULL
      )
    ''')
    conn.commit()
  
  cursor.execute("""
    SELECT COUNT(*)
    FROM sqlite_master
    WHERE type='table' AND name='attractions_topic'
  """)
  if not cursor.fetchone()[0] > 0:
    if initTableStr:
      initTableStr += ","
    initTableStr += "attractions_topic"
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS attractions_topic (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attId INTEGER NOT NULL,
        name TEXT NOT NULL
      )
    ''')
    conn.commit()
  
  cursor.execute("""
    SELECT COUNT(*)
    FROM sqlite_master
    WHERE type='table' AND name='attractions_comment'
  """)
  if not cursor.fetchone()[0] > 0:
    if initTableStr:
      initTableStr += ","
    initTableStr += "attractions_comment"
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS attractions_comment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attId INTEGER NOT NULL,
        memberId INTEGER,
        title TEXT,
        content TEXT,
        evaluate INTEGER,
        createTime DATE NOT NULL
      )
    ''')
    conn.commit()

  cursor.execute("""
      SELECT COUNT(*)
      FROM sqlite_master
      WHERE type='table' AND name='attractions_image'
    """)
  if not cursor.fetchone()[0] > 0:
    if initTableStr:
      initTableStr += ","
    initTableStr += "attractions_image"
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS attractions_image (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attId INTEGER NOT NULL,
        image TEXT NOT NULL,
        createTime DATE NOT NULL
      )
    ''')
    conn.commit()
  
  cursor.execute("""
    SELECT COUNT(*)
    FROM sqlite_master
    WHERE type='table' AND name='food'
  """)
  if not cursor.fetchone()[0] > 0:
    if initTableStr:
      initTableStr += ","
    initTableStr += "food"
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS food (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        content TEXT NOT NULL,
        postalCode TEXT,
        city TEXT,
        district TEXT,
        address TEXT,
        phone1 TEXT,
        phone2 TEXT,
        facilities TEXT,
        createTime DATE NOT NULL
      )
    ''')
    conn.commit()
  
  cursor.execute("""
    SELECT COUNT(*)
    FROM sqlite_master
    WHERE type='table' AND name='food_topic'
  """)
  if not cursor.fetchone()[0] > 0:
    if initTableStr:
      initTableStr += ","
    initTableStr += "food_topic"
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS food_topic (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        foodId INTEGER NOT NULL,
        name TEXT NOT NULL
      )
    ''')
    conn.commit()
  
  cursor.execute("""
    SELECT COUNT(*)
    FROM sqlite_master
    WHERE type='table' AND name='food_comment'
  """)
  if not cursor.fetchone()[0] > 0:
    if initTableStr:
      initTableStr += ","
    initTableStr += "food_comment"
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS food_comment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        foodId INTEGER NOT NULL,
        memberId INTEGER,
        title TEXT,
        content TEXT,
        evaluate INTEGER,
        createTime DATE NOT NULL
      )
    ''')
    conn.commit()

  cursor.execute("""
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type='table' AND name='food_image'
      """)
  if not cursor.fetchone()[0] > 0:
    if initTableStr:
      initTableStr += ","
    initTableStr += "food_image"
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS food_image (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        foodId INTEGER NOT NULL,
        image TEXT NOT NULL,
        createTime DATE NOT NULL
      )
    ''')
    conn.commit()
  
  conn.close()
  return initTableStr

if __name__ == '__main__':
  initStr = init_db()
  if initStr:
    print(f" * SQLITE 資料庫已初始化，初始化的資料表：{initStr}")