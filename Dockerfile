FROM ubuntu:22.04

WORKDIR /root/app
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y python3 python3-pip

RUN cp /usr/bin/python3 /usr/bin/python

COPY requirements.* ./
RUN pip install -r requirements.chill.txt

COPY ./ ./

CMD python3 infi_while.py
