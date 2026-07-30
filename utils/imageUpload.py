import os
import base64
from io import BytesIO
from datetime import datetime
import secrets

from PIL import Image


def save_image(
  image_data: dict,
  upload_folder: str,
  thumbnail_folder: str,
  thumbnail_size=(400, 300),
):
  """
  儲存圖片並建立縮圖

  Parameters
  ----------
  image_data : dict
    {
      "filename": "abc.jpg",
      "content": "data:image/jpeg;base64,..."
    }

  upload_folder : str
    原圖資料夾

  thumbnail_folder : str
    縮圖資料夾

  thumbnail_size : tuple
    縮圖尺寸

  Returns
  -------
  str
    新檔名
  """

  if not image_data:
    return None

  os.makedirs(upload_folder, exist_ok=True)
  os.makedirs(thumbnail_folder, exist_ok=True)

  # 副檔名
  ext = os.path.splitext(image_data["filename"])[1].lower()

  if ext == "":
      ext = ".jpg"

  # 新檔名
  # yyyyMMddHHmmssffffff+隨機碼3碼
  filename = (
    datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
    + "_"
    + secrets.token_hex(3)
    + ext
  )

  upload_path = os.path.join(upload_folder, filename)

  thumbnail_path = os.path.join(thumbnail_folder, filename)

  # Base64 -> Image
  base64_str = image_data["content"]

  if "," in base64_str:
    base64_str = base64_str.split(",")[1]

  image_bytes = base64.b64decode(base64_str)
  image = Image.open(BytesIO(image_bytes))

  # 儲存原圖
  image.save(upload_path)

  # 建立縮圖
  thumb = image.copy()
  thumb.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
  thumb.save(thumbnail_path)

  return filename
