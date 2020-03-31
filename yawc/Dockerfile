FROM python:3
RUN apt-get update -y
RUN apt-get install -y zip
RUN pip install scrapy psycopg2-binary boto3 click
WORKDIR /yawc
COPY . /yawc
ENTRYPOINT ["./main.sh"]