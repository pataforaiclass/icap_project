from functools import wraps
from flask import session, jsonify, redirect, url_for

def login_required(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    if not session.get("is_login"):
      return redirect(url_for("web.front.loginPage"))
    return func(*args, **kwargs)
  return wrapper

def manager_required(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    if not session.get("manager_login"):
      return redirect(url_for("web.admin.loginPage"))
    return func(*args, **kwargs)
  return wrapper

def api_login_required(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    if not session.get("is_login"):
      return jsonify({
        "message": "請先登入"
      }), 401
    return func(*args, **kwargs)
  return wrapper

def api_manager_required(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    if not session.get("manager_login"):
      return jsonify({
        "message": "請先登入"
      }), 401
    return func(*args, **kwargs)
  return wrapper