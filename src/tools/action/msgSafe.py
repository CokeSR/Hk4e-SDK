# ===================== 信息脱敏 ===================== #
def mask_string(text):
    if len(text) < 4:
        return "*" * len(text)  # 如果源小于4个字符，则将其全部屏蔽
    else:
        start_pos = 2 if len(text) >= 10 else 1  # 根据总长度，显示1或2个第一个字符
        end_post = (
            2 if len(text) > 5 else 1
        )  # 显示最后2个字符，但前提是总长度大于5个字符
        return f"{text[0:start_pos]}****{text[len(text)-end_post:]}"


def mask_identity(text):
    length = len(text)
    if length == 2:  # 名字是二字，返回 *名
        return f"{'*' + text[-1]}"
    if length == 3:  # 名字是三字或以上 返回第一个字 * 最后一个字
        return f"{text[0] + '*' + text[-1]}"
    if length == 18:  # 身份证号，显示前三位和后三位
        return f"{text[:3] + '*' * len(text[3:-3]) + text[-3:]}"
    else:
        return mask_string(text)


def mask_email(email):
    text = email.split("@")
    return f"{mask_string(text[0])}@{text[1]}"
