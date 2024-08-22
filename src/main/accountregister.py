try:
    from __main__ import app
except ImportError:
    from main import app
import re
import random
import string
import src.tools.repositories as repositories
from time import time as epoch
from src.tools.action.dbGet import get_db
from src.tools.action.mailSend import send_email_smtp
from src.tools.action.passwordManage import password_hash
from src.tools.loadconfig import get_config
from src.tools.response import json_rsp_with_msg
from flask import request, render_template, flash, session
from datetime import datetime, timedelta
from pytz import timezone

utz = timezone('UTC')
ctz = timezone('Asia/Shanghai')

# ===================== 注册模块 ===================== #
# 游戏账号注册
@app.route('/index.html', methods=['GET','POST'])
@app.route('/preapp/account-system-sea/geetestV2.html', methods=['GET', 'POST'])
@app.route('/preapp/account-system-sea/index.html',methods=['GET','POST'])
@app.route("/pcSdkLogin.html", methods=["GET", "POST"])
@app.route("/account/register", methods=["GET", "POST"])
@app.route("/mihoyo/common/accountSystemSandboxFE/index.html", methods=["GET", "POST"])
def account_register():
    session.permanent = True
    cursor = get_db().cursor()
    
    if request.method == "POST":
        username = request.form.get("username")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        verifycode = request.form.get("verifycode")
        password = request.form.get("password")
        passwordv2 = request.form.get("passwordv2")
        
        cursor.execute("SELECT * FROM `t_accounts` WHERE `mobile` = %s or `email` = %s", (mobile, email,))
        account_status = cursor.fetchone()
        
        if account_status:
            flash("账号已被注册，请重试手机号或邮箱", "error")
            return render_template("account/register.tmpl")
        
        if not re.fullmatch(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email):
            flash("邮箱格式不正确", "error")
            return render_template("account/register.tmpl")
        
        if not re.fullmatch(r"^\d{11}$", mobile):
            flash("手机号码格式不正确", "error")
            return render_template("account/register.tmpl")
        
        if get_config()["Mail"]["ENABLE"] and "register_codes" in session:
            valid = False
            for register_code_info in session["register_codes"]:
                if (
                    register_code_info["email"] == email
                    and register_code_info["verification_code"] == verifycode
                    and register_code_info["valid"]
                    and register_code_info["timeout"] >= datetime.now(utz)
                ):
                    valid = True
                    break
            
            if not valid:
                flash("验证码错误或失效", "error")
                return render_template("account/register.tmpl")
        
        if password != passwordv2:
            flash("两次输入的密码不一致", "error")
            return render_template("account/register.tmpl")
        
        if len(password) < get_config()["Security"]["min_password_len"]:
            flash(f"密码长度不能小于 {get_config()['Security']['min_password_len']} 字节", "error")
            return render_template("account/register.tmpl")
        
        cursor.execute(
            "INSERT INTO `t_accounts` (`name`, `mobile`, `email`, `password`, `type`, `epoch_created`) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                username,
                mobile,
                email,
                password_hash(password),
                repositories.ACCOUNT_TYPE_NORMAL,
                int(epoch()),
            ),
        )
        flash("游戏账号注册成功，请返回登录", "success")
    return render_template("account/register.tmpl")


# 邮件验证码 用于注册
@app.route("/account/register_code", methods=["POST"])
def register_code():
    session.permanent = True
    email = request.form.get("email")
    email_pattern = "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.match(email_pattern, email):
        return json_rsp_with_msg(repositories.RES_FAIL, "邮箱格式不正确", {})

    cursor = get_db().cursor()
    user_query = "SELECT * FROM `t_accounts` WHERE `email` = %s"
    cursor.execute(user_query, (email,))
    user = cursor.fetchone()

    if user:
        return json_rsp_with_msg(repositories.RES_FAIL, "邮箱已经被注册了", {})

    if "register_codes" in session:
        session["register_codes"] = [code for code in session["register_codes"] if code["timeout"] >= datetime.now(utz)]
        
        if len(session["register_codes"]) > 5:
            except_time = session["register_codes"][-6]["timeout"].astimezone(ctz).strftime("%Y-%m-%d %H:%M:%S")
            return json_rsp_with_msg(repositories.RES_FAIL, f"发送验证码频率超过限制，请在{except_time}后再试", {})

    if "send_code_timeout" in session and session["send_code_timeout"] > datetime.now(utz):
        except_time = session["send_code_timeout"].astimezone(ctz).strftime("%Y-%m-%d %H:%M:%S")
        return json_rsp_with_msg(repositories.RES_FAIL, f"发送验证码间隔为60秒，请在{except_time}后再试", {})

    verification_code = "".join(random.choices(string.digits, k=get_config()['Security']['verify_code_length']))

    if not send_email_smtp(verification_code, email):
        return json_rsp_with_msg(repositories.RES_FAIL, "发送邮件失败，请联系管理员", {})

    new_register_code_info = {
        "email": email,
        "verification_code": verification_code,
        "timeout": datetime.now(utz) + timedelta(seconds=300),
        "valid": True,
    }

    if "register_codes" in session:
        for register_code_info in session["register_codes"]:
            if register_code_info["email"] == email:
                register_code_info["valid"] = False
        session["register_codes"].append(new_register_code_info)
    else:
        session["register_codes"] = [new_register_code_info]

    session["send_code_timeout"] = datetime.now(utz) + timedelta(seconds=60)
    return json_rsp_with_msg(repositories.RES_SUCCESS, "验证码发送成功，请查收邮箱", {})
