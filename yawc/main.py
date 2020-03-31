import click

from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
import os
import boto3
import shutil

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', 'yawc')

AWS_SQS_URL = os.getenv('AWS_SQS_URL')

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_KEY,
)

sqs = boto3.client(
    'sqs',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_KEY,
)


def main():
    response = sqs.receive_message(
        QueueUrl=AWS_SQS_URL,
        MaxNumberOfMessages=1,
        VisibilityTimeout=10,
        WaitTimeSeconds=10,
    )

    if not ('Messages' in response) or not response['Messages']:
        exit(1)

    message = response['Messages'][0]
    filename = message['Body']
    handle = message['ReceiptHandle']

    sqs.delete_message(QueueUrl=AWS_SQS_URL, ReceiptHandle=handle)

    s3.download_file(AWS_S3_BUCKET, filename, filename)

    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    process = CrawlerProcess(get_project_settings())
    process.crawl('site_crawler', seed_file=filename)
    process.start() # the script will block here until the crawling is finished

    zip_filename = f'{filename}.zip'
    shutil.make_archive(filename, 'zip', './result')
    shutil.rmtree('./result')
    s3.upload_file(zip_filename, AWS_S3_BUCKET, zip_filename)
    os.remove(zip_filename)
    os.remove(filename)

if __name__ == '__main__':
    main() # pylint: disable=no-value-for-parameter
