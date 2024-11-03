try:
    from __main__ import app
except ImportError:
    from main import app

import re
import random
import string
import src.tools.repositories as repositories

from flask                           import request, render_template, flash, session
from datetime                        import datetime, timedelta, timezone
from src.tools.loadconfig            import loadConfig
from src.tools.response              import jsonRspWithMsg
from src.tools.action.dbGet          import getMysqlConn
from src.tools.action.mailSend       import sendEmailSmtp
from src.tools.action.passwordManage import passwordHash

ctz = timezone(timedelta(hours=8))
utz = timezone(timedelta(hours=0))

# ===================== 找回密码 ===================== #
# 找回密码(功能不可用)
@app.route("/account/recover", methods=["GET", "POST"])
def account_recover():
    session.permanent = True
    cursor = getMysqlConn().cursor()

    if request.method == "POST":
        email      = request.form.get("email")
        verifycode = request.form.get("verifycode")
        password   = request.form.get("password")
        passwordv2 = request.form.get("passwordv2")
        
        if not re.fullmatch(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email):
            flash("邮箱格式不正确", "error")
        else:
            cursor.execute("SELECT * FROM `t_accounts` WHERE `email` = %s", (email,))
            email_exists = cursor.fetchone()
            if not email_exists:
                flash("该邮箱不存在", "error")
            if loadConfig()["Mail"]["ENABLE"] and "recover_codes" in session:
                valid = False
                for recover_code_info in session["recover_codes"]:
                    if (
                        recover_code_info["email"] == email
                        and recover_code_info["verification_code"] == verifycode
                        and recover_code_info["valid"]
                        and recover_code_info["timeout"] >= datetime.now(utz)
                    ):
                        valid = True
            if valid is False:
                flash("验证码错误或失效", "error")
            if password != passwordv2:
                flash("两次输入的密码不一致", "error")
            if len(password) < loadConfig()["Security"]["min_password_len"]:
                flash(
                    f"密码长度不能小于 {loadConfig()['Security']['min_password_len']} 字节",
                    "error",
                )
            new_password = passwordHash(password)
            cursor.execute(
                "UPDATE `t_accounts` SET `password` = %s WHERE `email` = %s",
                (new_password, email),
            )
            flash("密码重置成功，请返回登录", "success")
    return render_template("account/recover.tmpl")


# 邮件验证码 用于找回密码
@app.route("/account/recover_code", methods=["POST"])
def recover_code():
    session.permanent = True
    email = request.form.get("email")
    email_pattern = "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.match(email_pattern, email):
        return jsonRspWithMsg(repositories.RES_FAIL, "邮箱格式不正确", {})
    
    cursor = getMysqlConn().cursor()
    user_query = "SELECT * FROM `t_accounts` WHERE `email` = %s"
    cursor.execute(user_query, (email,))
    user = cursor.fetchone()

    if not user:
        return jsonRspWithMsg(repositories.RES_FAIL, "该邮箱不存在", {})

    if "recover_codes" in session:
        session["recover_codes"] = [code for code in session["recover_codes"] if code["timeout"] >= datetime.now(utz)]
        
        if len(session["recover_codes"]) > 5:
            except_time = session["recover_codes"][-6]["timeout"].astimezone(ctz).strftime("%Y-%m-%d %H:%M:%S")
            return jsonRspWithMsg(repositories.RES_FAIL, f"发送验证码频率超过限制，请在{except_time}后再试", {})

    if "send_code_timeout" in session and session["send_code_timeout"] > datetime.now(utz):
        except_time = session["send_code_timeout"].astimezone(ctz).strftime("%Y-%m-%d %H:%M:%S")
        return jsonRspWithMsg(repositories.RES_FAIL, f"发送验证码间隔为60秒，请在{except_time}后再试", {})

    verification_code = "".join(random.choices(string.digits, k=loadConfig()['Security']['verify_code_length']))

    if not sendEmailSmtp(verification_code, email):
        return jsonRspWithMsg(repositories.RES_FAIL, "发送邮件失败，请联系管理员", {})
 
    new_register_code_info = {
        "email": email,
        "verification_code": verification_code,
        "timeout": datetime.now(utz) + timedelta(seconds=300),
        "valid": True,
    }

    if "recover_codes" in session:
        for register_code_info in session["recover_codes"]:
            if register_code_info["email"] == email:
                register_code_info["valid"] = False
        session["recover_codes"].append(new_register_code_info)
    else:
        session["recover_codes"] = [new_register_code_info]

    session["send_code_timeout"] = datetime.now(utz) + timedelta(seconds=60)
    return jsonRspWithMsg(repositories.RES_SUCCESS, "验证码发送成功，请查收邮箱", {})
