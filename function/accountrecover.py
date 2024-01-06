try:
    from __main__ import app
except ImportError:
    from main import app
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
from flask import request, render_template, flash, current_app, session
from datetime import datetime, timedelta

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
@app.context_processor
def inject_config():
    config = get_config()
    return {'config': config}

#=====================找回密码=====================#
# 找回密码(功能不可用)
@app.route('/account/recover', methods=['GET', 'POST'])
def account_recover():
    session.permanent = True
    cursor = get_db().cursor()
    # cached_data = cache.get(request.form.get('email'))
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
            elif get_config()['Mail']['ENABLE'] and 'recover_codes' in session:
                vaild = False
                for recover_code_info in session['recover_codes']:
                    if recover_code_info['email'] == email and recover_code_info['reset_code'] == verifycode and recover_code_info['vaild'] and recover_code_info["timeout"] >= datetime.now():
                        vaild = True
                if vaild is False:
                    flash('验证码错误或失效', 'error')
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
    session.permanent = True
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
    if 'recover_codes' in session:
        not_timeout_li = []
        except_time = datetime.max
        for n in range(len(session['recover_codes'])):
            recover_code_info = session['recover_codes'][n]
            if recover_code_info["timeout"] >= datetime.now():
                # 计数未超时的验证码，包括因为同一email重复获取而失效的
                not_timeout_li.append(n)
            else:
                # 删除超时的验证码
                del session['recover_codes'][n]
        if len(not_timeout_li) > 5:
            # 当未超时的验证码超过5个后限制发送新的验证码
            except_time = session['recover_codes'][not_timeout_li[-6]]["timeout"].strftime("%Y-%m-%d %H:%M:%S")
            return json_rsp_with_msg(repositories.RES_FAIL, f"发送验证码频率超过限制，请在{except_time}后再试", {})
    if 'send_code_timeout' in session and session['send_code_timeout'] < datetime.now():
        # 验证与上次成功发送验证码的间隔是否超过60秒
        except_time = session['send_code_timeout'].strftime("%Y-%m-%d %H:%M:%S")
        return json_rsp_with_msg(repositories.RES_FAIL, f"发送验证码间隔为60秒，请在{except_time}后再试", {})
    reset_code = ''.join(random.choices(string.digits, k=4))
    mail = current_app.extensions['mail']
    msg = Message(f"重置密码请求", recipients=[email])
    msg.body = f"您的重置密码验证码是：{reset_code}，验证码5分钟内有效"
    try:
        mail.send(msg)
    except:
        return json_rsp_with_msg(repositories.RES_FAIL, "未知异常，请联系管理员", {})
    recover_code_info = {
            "email": email,
            "verification_code": reset_code,
            "timeout": datetime.now() + timedelta(seconds=300),
            "valid": True
        }
    # 添加已发送验证码记录
    if 'recover_codes' in session:
        for n in range(len(session['recover_codes'])):
            recover_code_info = session['recover_codes'][n]
            if recover_code_info['email'] == email:
                # 将同一个email下的其他验证码标记为失效
                session['recover_codes'][n]['vaild'] = False
        session['recover_codes'].append(recover_code_info)
    else:
        session['recover_codes'] = [recover_code_info,]
    # 设置下次可以发送验证码的时间
    session['send_code_timeout'] = datetime.now() + timedelta(seconds=60)
    # cache.set(email, reset_code, timeout=60 * 5)
    return json_rsp_with_msg(repositories.RES_SUCCESS, "验证码发送成功，请查收邮箱", {})