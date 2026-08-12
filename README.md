# AI Travel Guide Website
## 專題簡介
本專題以「AI 輔助旅遊景點推薦平台」為題，使用 Bootstrap 製作 RWD 前端頁面，使用 Vue.js 呼叫 Flask API，並以 SQLite 儲存景點與分類資料。

網站使用者有訪客及管理員兩種身分，訪客可以瀏覽活動、景點及美食三大主題的資訊，以及查詢資訊和查看詳細內容，而管理員登入管理頁面之後能管理紀錄了前述三大主題資料表中的資料，並在管理頁顯示統計圖表。

## 使用技術
|類別|技術|
|:---|:---|
|前端|HTML、CSS、Bootstrap 5、Vue.js 3|
|UI / 元件|GLightbox、CKEditor 5|
|圖表|Chart.js|
|後端|Python、Flask|
|資料庫|SQLite 3|
|版本管理|Git、GitHub|

## 系統功能說明
|頁面或功能|說明|
|:---|:---|
|首頁|以一頁式導覽的格式顯示各個主題的區塊，並且能連結至各主題的列表。|
|列表|以卡片呈現資料，可使用關鍵字及分類查詢，並支援排序與分頁。|
|詳細內容|顯示單一資料的圖片、名稱、城市、分類、介紹文字與建立時間。|
|燈箱|點擊圖片能在同一頁面中放大檢視，若有多張圖片還能如幻燈片般切換。|
|簡易管理功能|可新增、修改、刪除資料資料，並有表單欄位檢查與操作回饋。|
|統計圖表|從後端 API 取得統計資料，使用 Chart.js 顯示各城市景點數量與各分類景點比例。|

### 截圖說明
實際截圖放在 `static/screenshots/` 資料夾，檔名如下：

|檔名|說明|
|:--|:--|
|index.png|首頁畫面|
|attractions.png|景點列表、搜尋、篩選、排序、分頁畫面|
|detail.png|景點詳細內容畫面|
|admin.png|管理頁管理員個人資訊及統計圖表畫面|
|admin_list.png|管理頁景點列表畫面|
|admin_edit.png|管理頁修改資料畫面|
|rwd-1200.png|桌機寬度 1200px|
|rwd-768.png|平板寬度 768px|
|rwd-375.png|手機寬度 375px|

### 專案畫面截圖
首頁

![首頁畫面](/static/screenshots/index.png)

列表

![景點列表](/static/screenshots/attractions.png)

詳細內容

![詳細內容](/static/screenshots/detail.png)

管理頁及圖表

![管理頁](/static/screenshots/admin.png)

管理頁景點列表

![管理頁景點列表](/static/screenshots/admin_list.png)

管理頁修改資料

![管理頁修改資料](/static/screenshots/admin_edit.png)

桌機寬度 1200px 截圖

![景點列表](/static/screenshots/rwd-1200.png)

平板寬度 768px 截圖

![景點列表](/static/screenshots/rwd-768.png)

手機寬度 375px 截圖

![景點列表](/static/screenshots/rwd-375.png)

## 資料庫設計說明
本專題使用 SQLite，資料庫檔案為 database.db。程式啟動時會自動建立資料表與預設資料。

### event 年度活動資料表
|欄位|型別|說明|
|:---|:---|:---|
|id|INTEGER|主鍵，自動編號|
|title|TEXT|活動標題，不可為空值|
|content|TEXT|活動內容，不可為空值|
|organizer|TEXT|主辦單位|
|postalCode|TEXT|郵遞區號|
|city|TEXT|城市|
|district|TEXT|鄉鎮區域|
|address|TEXT|地址|
|createTime|DATE|建立日期，不可為空值|

### event_image 年度活動圖片
|欄位|型別|說明|
|:---|:---|:---|
|id|INTEGER|主鍵，自動編號|
|eventId|INTEGER|活動編號，不可為空值，對應`event.id`|
|image|TEXT|圖片檔名，不可為空值|
|createTime|DATE|建立日期，不可為空值|

### attractions 熱門景點資料表
|欄位|型別|說明|
|:---|:---|:---|
|id|INTEGER|主鍵，自動編號|
|title|TEXT|景點標題，不可為空值|
|content|TEXT|景點簡介，不可為空值|
|postalCode|TEXT|郵遞區號|
|city|TEXT|城市|
|district|TEXT|鄉鎮區域|
|address|TEXT|地址|
|tip|TEXT|旅遊叮嚀|
|facilities|TEXT|服務設施|
|createTime|DATE|建立日期，不可為空值|

### attractions_topic 熱門景點分類
|欄位|型別|說明|
|:---|:---|:---|
|id|INTEGER|主鍵，自動編號|
|attId|INTEGER|景點編號，不可為空值，對應`attractions.id`|
|name|TEXT|分類名稱，不可為空值|

### attractions_image 熱門景點圖片
|欄位|型別|說明|
|:---|:---|:---|
|id|INTEGER|主鍵，自動編號|
|attId|INTEGER|景點編號，不可為空值，對應`attractions.id`|
|image|TEXT|圖片檔名，不可為空值|
|createTime|DATE|建立日期，不可為空值|

### food 美食巡禮資料表
|欄位|型別|說明|
|:---|:---|:---|
|id|INTEGER|主鍵，自動編號|
|title|TEXT|店家標題，不可為空值|
|content|TEXT|店家簡介，不可為空值|
|postalCode|TEXT|郵遞區號|
|city|TEXT|城市|
|district|TEXT|鄉鎮區域|
|address|TEXT|地址|
|phone1|TEXT|店家電話1|
|phone2|TEXT|店家電話2|
|facilities|TEXT|服務設施|
|createTime|DATE|建立日期，不可為空值|

### food_topic 美食巡禮分類
|欄位|型別|說明|
|:---|:---|:---|
|id|INTEGER|主鍵，自動編號|
|foodId|INTEGER|店家編號，不可為空值，對應`food.id`|
|name|TEXT|分類名稱，不可為空值|

### food_image 美食巡禮圖片
|欄位|型別|說明|
|:---|:---|:---|
|id|INTEGER|主鍵，自動編號|
|foodId|INTEGER|店家編號，不可為空值，對應`food.id`|
|image|TEXT|圖片檔名，不可為空值|
|createTime|DATE|建立日期，不可為空值|

### manager 管理員帳號資訊
|欄位|型別|說明|
|:---|:---|:---|
|id|INTEGER|主鍵，自動編號|
|account|TEXT|帳號，不可為空值，不可重複|
|pwd|TEXT|密碼，不可為空值，存入資料庫前會先加密|
|userName|TEXT|用戶名稱，不可為空值|
|email|TEXT|電子信箱，不可為空值|
|mobile|TEXT|電話或手機號碼|
|createTime|DATE|建立日期，不可為空值|

## API 說明
API 成功時會回傳 message 與資料內容；失敗時會回傳錯誤原因及錯誤代碼。

|方法|路徑|功能|前端使用位置|
|:---|:---|:---|:---|
|GET|`/admin/api/index`|獲取管理頁面圖表所需統計資料及管理者個人用戶資料|管理頁面|
|---|
|GET|`/admin/api/event`|獲取 event 資料表所有資料及計算每筆資料下有多少圖片|管理頁面|
|GET|`/admin/api/event/<id>`|獲取 event 資料表中單一資料及所有與之關聯的圖片|管理頁面|
|POST|`/admin/api/event`|在 event 資料表中新增一筆資料及相關圖片|管理頁面|
|PATCH|`/admin/api/event/<id>`|修改所有 event 資料表中單一資料及圖片|管理頁面|
|DELETE|`/admin/api/event/<id>/img/<imgFileName>`|刪除特定圖片|管理頁面|
|DELETE|`/admin/api/event/<id>`|刪除特定資料及相關圖片|管理頁面|
|---|
|GET|`/admin/api/attr`|獲取 attractions 資料表所有資料及相關分類和計算每筆資料下有多少圖片|管理頁面|
|GET|`/admin/api/attr/<id>`|獲取 attractions 資料表中單一資料及相關分類和圖片|管理頁面|
|POST|`/admin/api/attr`|在 attractions 資料表中新增一筆資料及相關分類和圖片|管理頁面|
|PATCH|`/admin/api/attr/<id>`|修改所有 attractions 資料表中單一資料及相關分類和圖片|管理頁面|
|DELETE|`/admin/api/attr/<id>/img/<imgFileName>`|刪除特定圖片|管理頁面|
|DELETE|`/admin/api/attr/<id>`|刪除特定資料及相關分類和圖片|管理頁面|
|---|
|GET|`/admin/api/food`|獲取 food 資料表所有資料及相關分類和計算每筆資料下有多少圖片|管理頁面|
|GET|`/admin/api/food/<id>`|獲取 food 資料表中單一資料及相關分類和圖片|管理頁面|
|POST|`/admin/api/food`|在 food 資料表中新增一筆資料及相關分類和圖片|管理頁面|
|PATCH|`/admin/api/food/<id>`|修改所有 food 資料表中單一資料及相關分類和圖片|管理頁面|
|DELETE|`/admin/api/food/<id>/img/<imgFileName>`|刪除特定圖片|管理頁面|
|DELETE|`/admin/api/food/<id>`|刪除特定資料及相關分類和圖片|管理頁面|
|---|
|GET|`/api/index`|獲取首頁所需資料|訪客頁面|
|GET|`/api/event`|獲取 event 列表所需資訊|訪客頁面|
|GET|`/api/event/<id>`|獲取 event 資料表中單一資料的詳細資訊|訪客頁面|
|GET|`/api/attr`|獲取 attractions 列表所需資訊|訪客頁面|
|GET|`/api/attr/<id>`|獲取 attractions 資料表中單一資料的詳細資訊|訪客頁面|
|GET|`/api/food`|獲取 food 列表所需資訊|訪客頁面|
|GET|`/api/food/<id>`|獲取 food 資料表中單一資料的詳細資訊|訪客頁面|

## AI 功能說明
本專題利用 AI 輔助功能協助網站美工、及生成部分景點及美食店家介紹內容。

|使用情境|Prompt 範例|產出用途|
|:---|:---|:---|
|網站 Logo|請以「台中旅遊網站」為主題，生成一個合適的 Logo 圖片|置於網站 navbar 及 footer|
|景點介紹|請根據網路上現有的資訊寫出台中市彩虹眷村 1000 字以內的介紹。|放入景點介紹欄位|

## 測試紀錄
|日期|測試項目|測試方法|結果|
|:---|:---|:---|:---|
|8/11|訪客頁面 API|呼叫 `GET /api/event/10`|回傳活動詳細資料以及圖片|
|8/11|管理頁面 API|呼叫 `GET /admin/api/index`|回傳管理者個人用戶資料及圖表統計資料|

## Render 部署說明
本專案部署在 Render Web Service，讓前端頁面與 Flask API 皆能在線上展示。

### Render 建立服務時的設定
|欄位|設定|
|:---|:---|
|Service Type|Web Service|
|Runtime|Python 3|
|Branch|main|
|Build Command|pip install -r requirements.txt|
|Start Command|gunicorn app:app|
|Root Directory|空白，因為專案檔案在 Repository 根目錄|

### Python 版本
專案根目錄已加入 .python-version，Render 會依照此檔案使用 Python 3.13。

### SQLite 注意事項
Render 免費服務的檔案系統不是永久保存空間，所以 database.db 會在服務啟動時自動建立，每次服務重啟時皆會還原資料庫內容。

測試用管理員帳號： dsa

測試用管理員密碼： asd123asd

## 開發者資訊
|項目|內容|
|:---|:---|
|開發者|陳禹樵|
|專案名稱|AI Travel Guide Website|
|GitHub Repository|[https://github.com/RichieChen222333/AI-Travel-Guide](https://github.com/pataforaiclass/icap_project/)|
