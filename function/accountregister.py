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
from flask import request, render_template, flash, current_app, session
from datetime import datetime, timedelta

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
    session.permanent = True
    cursor = get_db().cursor()
    # cached_data = cache.get(request.form.get('email'))
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
        elif get_config()['Mail']['ENABLE'] and 'register_codes' in session:
            vaild = False
            for register_code_info in session['register_codes']:
                if register_code_info['email'] == email and register_code_info['verification_code'] == verifycode and register_code_info['vaild'] and register_code_info["timeout"]>=datetime.now():
                    vaild = True
            if vaild is False:
                flash('验证码错误或失效', 'error')
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
    session.permanent = True
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
    if 'register_codes' in session:
        not_timeout_li = []
        except_time = datetime.max
        for n in range(len(session['register_codes'])):
            register_code_info = session['register_codes'][n]
            if register_code_info["timeout"] >= datetime.now():
                # 计数未超时的验证码，包括因为同一email重复获取而失效的
                not_timeout_li.append(n)
            else:
                # 删除超时的验证码
                del session['register_codes'][n]
        if len(not_timeout_li) > 5:
            # 当未超时的验证码超过5个后限制发送新的验证码
            except_time = session['register_codes'][not_timeout_li[-6]]["timeout"].strftime("%Y-%m-%d %H:%M:%S")
            return json_rsp_with_msg(repositories.RES_FAIL, f"发送验证码频率超过限制，请在{except_time}后再试", {})
    if 'send_code_timeout' in session and session['send_code_timeout'] < datetime.now():
        # 验证与上次成功发送验证码的间隔是否超过60秒
        except_time = session['send_code_timeout'].strftime("%Y-%m-%d %H:%M:%S")
        return json_rsp_with_msg(repositories.RES_FAIL, f"发送验证码间隔为60秒，请在{except_time}后再试", {})
    verification_code = ''.join(random.choices(string.digits, k=4))
    mail = current_app.extensions['mail']
    msg = Message(f"注册验证", recipients=[email])
    msg.body = f"你的注册验证码是：{verification_code}，验证码5分钟内有效"
    try:
        mail.send(msg)
    except:
        return json_rsp_with_msg(repositories.RES_FAIL, "未知异常，请联系管理员", {})
    register_code_info = {
            "email": email,
            "verification_code": verification_code,
            "timeout": datetime.now() + timedelta(seconds=300),
            "valid": True
        }
    # 添加已发送验证码记录
    if 'register_codes' in session:
        for n in range(len(session['register_codes'])):
            register_code_info = session['register_codes'][n]
            if register_code_info['email'] == email:
                # 将同一个email下的其他验证码标记为失效
                session['register_codes'][n]['vaild'] = False
        session['register_codes'].append(register_code_info)
    else:
        session['register_codes'] = [register_code_info,]
    # 设置下次可以发送验证码的时间
    session['send_code_timeout'] = datetime.now() + timedelta(seconds=60)
    #cache.set(email, verification_code, timeout=60*5)
    return json_rsp_with_msg(repositories.RES_SUCCESS, "验证码发送成功，请查收邮箱", {})
