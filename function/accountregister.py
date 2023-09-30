from __main__ import app
import re
import random
import string
import settings.repositories as repositories

from time import time as epoch
from flask_mail import Message
from flask_caching import Cache
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

#=====================注册模块=====================#
# 游戏账号注册
@app.route('/account/register', methods=['GET', 'POST'])
@app.route('/mihoyo/common/accountSystemSandboxFE/index.html', methods=['GET', 'POST'])         # 国内沙箱 注册和找回URL是同一个
def account_register():
    cursor = get_db().cursor()
    cached_data = cache.get(request.form.get('email'))
    if request.method == 'POST':
        username = request.form.get('username')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        verifycode = request.form.get('verifycode')
        password = request.form.get('password')
        passwordv2 = request.form.get('passwordv2')
        cursor.execute("SELECT * FROM `t_accounts` WHERE `name` = %s", (username,))
        user = cursor.fetchone()
        if user:
            flash('您准备注册的用户名已被使用', 'error')
        cursor.execute("SELECT * FROM `t_accounts` WHERE `mobile` = %s", (mobile,))
        phone_number = cursor.fetchone()
        if phone_number:
            flash('电话号码已经被注册了', 'error')
        cursor.execute("SELECT * FROM `t_accounts` WHERE `email` = %s", (email,))
        email_exists = cursor.fetchone()
        if email_exists:
            flash('邮箱已经被注册了', 'error')
        elif not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            flash('邮箱格式不正确', 'error')
        elif not re.fullmatch(r'^\d{11}$', mobile):
            flash('手机号码格式不正确', 'error')
        elif verifycode != cached_data and get_config()['Mail']['ENABLE']:
            flash('验证码错误', 'error')
        elif password != passwordv2:
            flash('两次输入的密码不一致', 'error')
        elif len(password) < get_config()["Security"]["min_password_len"]:
            flash(f"密码长度不能小于 {get_config()['Security']['min_password_len']} 字节", 'error')
        else:
            cursor.execute("INSERT INTO `t_accounts` (`name`, `mobile`, `email`, `password`, `type`, `epoch_created`) "
                           "VALUES (%s, %s, %s, %s, %s, %s)",
                           (username, mobile, email, password_hash(password), repositories.ACCOUNT_TYPE_NORMAL, int(epoch())))
            flash('游戏账号注册成功，请返回登录', 'success')
            cache.delete(email)
    return render_template("account/register.tmpl")

# 邮件验证码 用于注册
@app.route('/account/register_code', methods=['POST'])
def register_code():
    email = request.form.get('email')
    email_pattern = '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if not re.match(email_pattern, email):
        return json_rsp_with_msg(repositories.RES_FAIL, "邮箱格式不正确", {})
    cursor = get_db().cursor()
    user_query = "SELECT * FROM `t_accounts` WHERE `email` = %s"
    cursor.execute(user_query, (email,))
    user = cursor.fetchone()
    if user:
        return json_rsp_with_msg(repositories.RES_FAIL, "邮箱已经被注册了", {})
    verification_code = ''.join(random.choices(string.digits, k=4))
    mail = current_app.extensions['mail']
    msg = Message(f"注册验证", recipients=[email])
    msg.body = f"你的注册验证码是：{verification_code}，验证码5分钟内有效"
    try:
        mail.send(msg)
    except:
        return json_rsp_with_msg(repositories.RES_FAIL, "未知异常，请联系管理员", {})
    cache.set(email, verification_code, timeout=60*5)
    return json_rsp_with_msg(repositories.RES_SUCCESS, "验证码发送成功，请查收邮箱", {})
