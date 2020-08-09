FROM python:3.8-slim

#RUN apt update
#RUN apt install build-essential -y
#RUN apt install emacs -y

COPY requirements.txt /

RUN pip install --no-cache-dir -r /requirements.txt

COPY * /app/
COPY portnoy/* /app/

WORKDIR /app
