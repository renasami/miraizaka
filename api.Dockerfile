FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

ENV LANG C.UTF-8
ENV TZ Asia/Tokyo
ENV PYTHONPATH=/

# pip installs
COPY ./api/app /app
COPY ./face_ee_manager /app/face_ee_manager
COPY ./api/requirements.txt requirements.txt
RUN apt-get update && apt-get upgrade -y
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN apt-get install -y libgl1-mesa-dev libglib2.0-dev
RUN pip install -r requirements.txt

# 開発用
COPY ./api/start.sh /start.sh
RUN chmod +x /start.sh

WORKDIR /app

EXPOSE 80