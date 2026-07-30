from flask import Blueprint, render_template
from routes.front.api import attractions as attr, event, food, member

bp = Blueprint('front', __name__)

bp.register_blueprint(attr.bp, url_prefix="/api/attr")
bp.register_blueprint(event.bp, url_prefix="/api/event")
bp.register_blueprint(food.bp, url_prefix="/api/food")
bp.register_blueprint(member.bp, url_prefix="/api/member")