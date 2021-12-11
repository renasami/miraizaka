FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

ENV LANG C.UTF-8
ENV TZ Asia/Tokyo
ENV PYTHONPATH=/

# pip installs
COPY ./api/app app
COPY ./api/requirements.txt requirements.txt
COPY ./api/start.sh /start.sh
RUN chmod +x /start.sh
RUN apt-get update && apt-get upgrade -y
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN apt-get install -y libgl1-mesa-dev
RUN pip install -r requirements.txt

WORKDIR /app



EXPOSE 80