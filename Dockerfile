# 纯SDK环境
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /opt/hk4e/sdkserver/
RUN pip install --no-cache-dir -r /opt/hk4e/sdkserver/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /opt/hk4e/sdkserver
EXPOSE 21000
# 生产环境运行
# CMD ['gunicorn','-w', '4', '-b', 'ip_address:port', 'main:launch()', '--access-logfile', 'logs/sdkserver.log', '--error-logfile', 'logs/sdkserver-error.log']
CMD [ "python", "./main.py", "serve" ]
