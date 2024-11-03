try:
    from __main__ import app
except ImportError:
    from main import app

import re
import random
import string
import src.tools.repositories as repositories

from flask                           import request, render_template, flash, session
from time                            import time                as epoch
from pytz                            import timezone
from datetime                        import datetime, timedelta
from src.tools.loadconfig            import loadConfig
from src.tools.response              import jsonRspWithMsg
from src.tools.logger.user           import logger              as user_log
from src.tools.logger.system         import logger              as sys_log
from src.tools.action.dbGet          import getMysqlConn
from src.tools.action.mailSend       import sendEmailSmtp
from src.tools.action.passwordManage import passwordHash

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
    cursor = getMysqlConn().cursor()
    
    if request.method == "POST":
        username   = request.form.get("username")
        mobile     = request.form.get("mobile")
        email      = request.form.get("email")
        verifycode = request.form.get("verifycode")
        password   = request.form.get("password")
        passwordv2 = request.form.get("passwordv2")
        
        user_log.info(f"主机 {request.remote_addr} 用户: {username} 邮箱: {email} 手机: {mobile} 尝试注册账号")
        
        cursor.execute("SELECT * FROM `t_accounts` WHERE `mobile` = %s or `email` = %s", (mobile, email,))
        account_status = cursor.fetchone()
        
        if account_status:
            user_log.warning(f"主机 {request.remote_addr} 用户: {username} 注册账号失败：已存在")
            flash("账号已被注册，请重试手机号或邮箱", "error")
            return render_template("account/register.tmpl", config=loadConfig())
        
        if not re.fullmatch(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email):
            user_log.warning(f"主机 {request.remote_addr} 用户: {username} 注册账号失败：邮箱格式非法")
            flash("邮箱格式不正确", "error")
            return render_template("account/register.tmpl", config=loadConfig())
        
        if not re.fullmatch(r"^\d{11}$", mobile):
            user_log.warning(f"主机 {request.remote_addr} 用户: {username} 注册账号失败：手机号非法")
            flash("手机号码格式不正确", "error")
            return render_template("account/register.tmpl", config=loadConfig())
        
        if loadConfig()["Mail"]["ENABLE"] and "register_codes" in session:
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
                user_log.warning(f"主机 {request.remote_addr} 用户: {username} 注册账号失败：无效的验证码")
                flash("验证码错误或失效", "error")
                return render_template("account/register.tmpl", config=loadConfig())

        if password != passwordv2:
            user_log.warning(f"主机 {request.remote_addr} 用户: {username} 注册账号失败：密码不一致")
            flash("两次输入的密码不一致", "error")
            return render_template("account/register.tmpl", config=loadConfig())
        
        if len(password) < loadConfig()["Security"]["min_password_len"]:
            user_log.warning(f"主机 {request.remote_addr} 用户: {username} 注册账号失败：密码长度小于系统预设")
            flash(f"密码长度不能小于 {loadConfig()['Security']['min_password_len']} 字节", "error")
            return render_template("account/register.tmpl", config=loadConfig())
        
        cursor.execute(
            "INSERT INTO `t_accounts` (`name`, `mobile`, `email`, `password`, `type`, `epoch_created`) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                username,
                mobile,
                email,
                passwordHash(password),
                repositories.ACCOUNT_TYPE_NORMAL,
                int(epoch()),
            ),
        )
        user_log.info(f"主机 {request.remote_addr} 用户: {username} 邮箱: {email} 手机: {mobile} 注册账号成功")
        flash("游戏账号注册成功，请返回登录", "success")
    return render_template("account/register.tmpl", config=loadConfig())


# 邮件验证码 用于注册
@app.route("/account/register_code", methods=["POST"])
def register_code():
    session.permanent = True
    email         = request.form.get("email")
    email_pattern = "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    
    if not re.match(email_pattern, email):
        sys_log.info(f"主机 {request.remote_addr} 注册邮箱：{email}, 尝试发送验证码失败：格式非法")
        return jsonRspWithMsg(repositories.RES_FAIL, "邮箱格式不正确", {})

    cursor = getMysqlConn().cursor()
    user_query = "SELECT * FROM `t_accounts` WHERE `email` = %s"
    cursor.execute(user_query, (email,))
    user = cursor.fetchone()

    if user:
        sys_log.info(f"主机 {request.remote_addr} 注册邮箱：{email}, 尝试发送验证码失败：已存在")
        return jsonRspWithMsg(repositories.RES_FAIL, "邮箱已经被注册了", {})

    if "register_codes" in session:
        session["register_codes"] = [code for code in session["register_codes"] if code["timeout"] >= datetime.now(utz)]
        
        if len(session["register_codes"]) > 5:
            except_time = session["register_codes"][-6]["timeout"].astimezone(ctz).strftime("%Y-%m-%d %H:%M:%S")
            sys_log.error(f"主机 {request.remote_addr} 注册邮箱：{email}, 尝试发送验证码失败：频率限制")
            return jsonRspWithMsg(repositories.RES_FAIL, f"发送验证码频率超过限制，请在{except_time}后再试", {})

    if "send_code_timeout" in session and session["send_code_timeout"] > datetime.now(utz):
        except_time = session["send_code_timeout"].astimezone(ctz).strftime("%Y-%m-%d %H:%M:%S")
        sys_log.error(f"主机 {request.remote_addr} 注册邮箱：{email}, 尝试发送验证码失败：仍在有效期")
        return jsonRspWithMsg(repositories.RES_FAIL, f"发送验证码间隔为60秒，请在{except_time}后再试", {})

    # 验证码生成 | 基于config 配置长度
    verification_code = "".join(random.choices(string.digits, k=loadConfig()['Security']['verify_code_length']))
    
    if not sendEmailSmtp(verification_code, email):
        sys_log.error(f"主机 {request.remote_addr} 注册邮箱：{email}, 尝试发送验证码失败：系统错误")
        return jsonRspWithMsg(repositories.RES_FAIL, "发送邮件失败，请联系管理员", {})

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

    sys_log.info(f"主机 {request.remote_addr} 注册邮箱：{email}, 尝试发送验证码成功：{verification_code}")
    return jsonRspWithMsg(repositories.RES_SUCCESS, "验证码发送成功，请查收邮箱", {})
