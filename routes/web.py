from flask import Blueprint, redirect, url_for, render_template
from routes.admin import index as admin
from routes.front import index as front

bp = Blueprint('web', __name__)

bp.register_blueprint(admin.bp, url_prefix="/admin")
bp.register_blueprint(front.bp)

# 首頁
@bp.route("/")
def toIndex():
  return redirect(url_for("index"))

@bp.route("/index")
def index():
  return render_template(
    "front/index.html",
    current_page="index"
  )

# 美食巡禮
@bp.route("/event")
def eventPage():
    return render_template(
        "front/event.html",
        current_page="event"
    )

# 美食巡禮
@bp.route("/attr")
def attrPage():
    return render_template(
        "front/attractions.html",
        current_page="attractions"
    )

# 美食巡禮
@bp.route("/food")
def foodPage():
    return render_template(
        "front/food.html",
        current_page="food"
    )