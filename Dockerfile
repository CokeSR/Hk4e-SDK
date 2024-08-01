FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir werkzeug==2.2.3 flask==2.2.4 flask_mail Flask-Caching==2.0.2 requests rsa geoip2 bcrypt pyyaml pymysql protobuf cryptography Flask-Limiter gunicorn cachetools redis -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /opt/hk4e/sdkserver
EXPOSE 21000
CMD [ "python", "./main.py", "serve" ]
