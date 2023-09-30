from __main__ import app
import re
import random
import string
import settings.repositories as repositories

from flask_caching import Cache
from flask_mail import Message
from settings.database import get_db
from settings.library import password_hash
from settings.loadconfig import get_config
from settings.response import json_rsp_with_msg
from flask import request, render_template, flash, current_app

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
@app.context_processor
def inject_config():
    config = get_config()
    return {'config': config}

#=====================找回密码=====================#
# 找回密码(功能不可用)
@app.route('/account/recover', methods=['GET', 'POST'])
def account_recover():
    cursor = get_db().cursor()
    cached_data = cache.get(request.form.get('email'))
    if request.method == 'POST':
        email = request.form.get('email')
        verifycode = request.form.get('verifycode')
        password = request.form.get('password')
        passwordv2 = request.form.get('passwordv2')
        if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            flash('邮箱格式不正确', 'error')
        else:
            cursor.execute("SELECT * FROM `t_accounts` WHERE `email` = %s", (email,))
            email_exists = cursor.fetchone()
            if not email_exists:
                flash('该邮箱不存在', 'error')
            elif verifycode != cached_data and get_config()['Mail']['ENABLE']:
                flash('验证码错误', 'error')
            elif password != passwordv2:
                flash('两次输入的密码不一致', 'error')
            elif len(password) < get_config()["Security"]["min_password_len"]:
                flash(f"密码长度不能小于 {get_config()['Security']['min_password_len']} 字节", 'error')
            else:
                new_password = password_hash(password)
                cursor.execute("UPDATE `t_accounts` SET `password` = %s WHERE `email` = %s",
                               (new_password, email))
                flash('密码重置成功，请返回登录', 'success')
                cache.delete(email)
    return render_template("account/recover.tmpl")

# 邮件验证码 用于找回密码
@app.route('/account/recover_code', methods=['POST'])
def recover_code():
    email = request.form.get('email')
    email_pattern = '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if not re.match(email_pattern, email):
        return json_rsp_with_msg(repositories.RES_FAIL, "邮箱格式不正确", {})
    cursor = get_db().cursor()
    user_query = "SELECT * FROM `t_accounts` WHERE `email` = %s"
    cursor.execute(user_query, (email,))
    user = cursor.fetchone()
    if not user:
        return json_rsp_with_msg(repositories.RES_FAIL, "该邮箱不存在", {})
    reset_code = ''.join(random.choices(string.digits, k=4))
    mail = current_app.extensions['mail']
    msg = Message(f"重置密码请求", recipients=[email])
    msg.body = f"您的重置密码验证码是：{reset_code}，验证码5分钟内有效"
    try:
        mail.send(msg)
    except:
        return json_rsp_with_msg(repositories.RES_FAIL, "未知异常，请联系管理员", {})
    cache.set(email, reset_code, timeout=60 * 5)
    return json_rsp_with_msg(repositories.RES_SUCCESS, "验证码发送成功，请查收邮箱", {})