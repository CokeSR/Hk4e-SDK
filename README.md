# Hk4e-SDK ver 1.3.4（github-main）

Python-Flask实现游戏登录验证(Python版本：3.9 / 3.10)
![image](https://blog.cokeserver.com/upload/photo.png)
最近更新日期：2024/08/22
更新地址：https://gitlab.cokeserver.com/Coke/Hk4e-SDK (fix分支)
## 本地使用说明

- 本SDK支持如下（更多功能开发中...）：
    - ##### SSL
        - 本 SDK 支持配置 https 访问
        - 将 config: ssl 调整为 True
        - 使用 SDK 自签证书或自备证书
    - ##### IP 黑名单拦截功能
        - 配置 config 中 Security: access_limits 即可设置单次IP访问限制
    - ##### 实名认证
        - 适配于 CBT3 客户端与 Live 客户端
    - ##### 分区 Dispatch
        - 适配于CBT 客户端与 Live 客户端
        - 将 config 中 Gateserver 与 Dispatch: List 项配置即可
    - ##### 高版本客户端的密码验证
        - 适用于3.2至3.4版本客户端
        - 需要与 myhbase.ini 进行 rsa 适配
        - 将 config 中 Auth: enable_password_verify 调整为true
    - ##### 游戏内外公告显示
        - 可以自行的设置内容显示（数据库记录）
        - 需要有一定的h5基础
        - 需要准备适当的尺寸的图片文件
    - ##### CDK 内部兑换
        - 配置服务端中的cdk_url
        - 将 config 中 cdkexchange 项设置为 true
    - ##### 邮件发送
        - 在 config 中配置你的邮件信息（POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV）
        - 将 config 中 Mail：ENABLE 项设置为true

## Docker 构建说明：

- 在 docker_launch 和 docker_build 文件中配置好正确的服务端路径
- 服务端目录推荐结构：
  ![image](https://blog.cokeserver.com/upload/package.png)
- 第一次启动时，请自行导入SDK所需的数据库文件
- 默认信息如表：

| MYSQL                    | SDKSERVER                              |
|--------------------------|----------------------------------------|
| Port：5000                | Port: 21000                            |
| Ip_address: 172.10.3.100 | Ip_address: 172.10.3.253               |
| Password：cokeserver2022  | Command: python main.py serve / initdb / check |


### 注意：
- 提供了适用于生产环境的命令：
    - python main.py check
    - python main.py initdb
    - gunicorn -w 4 -b ip_address:port 'main:launch()' --access-logfile logs/sdkserver.log --error-logfile logs/sdkserver-error.log

    注意：gunicorn只适用于 Linux 平台

    4 仅作为参考线程参数，实际请计算：cpu核心数 *2 + 1
## 每次更新所需环境可能变化 请留意requirements文件