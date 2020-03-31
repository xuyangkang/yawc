import os
import click
import boto3
import tempfile
import time

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', 'yawc')
AWS_REGION = os.getenv('AWS_REGION', 'ap-northeast-1')

AWS_SQS_URL = os.getenv('AWS_SQS_URL')

s3 = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_KEY,
)

sqs = boto3.client(
    'sqs',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_KEY,
)

def upload(lines, filename):
    with tempfile.NamedTemporaryFile() as temp:
        for line in lines:
            temp.write(line.encode())
        temp.flush()
        temp.seek(0)
        s3.upload_fileobj(temp, AWS_S3_BUCKET, filename)
        ns = time.time_ns()
        sqs.send_message(QueueUrl=AWS_SQS_URL, MessageBody=filename, MessageDeduplicationId=f'{filename}-{ns}', MessageGroupId='yawc')

@click.command()
@click.option("--max_line", default=1000, help="Number of lines in splitted file")
@click.option("--input_file", help="Oringinal input file")
def main(max_line, input_file):
    lines = []
    block_count = 0
    with open(input_file) as f:
        for line in f:
            lines.append(line)
            if len(lines) == max_line:
                upload(lines, f'{input_file}-{block_count}')
                lines = []
                block_count += 1

    if lines:
        upload(lines, f'{input_file}-{block_count}')


if __name__ == '__main__':
    main() # pylint: disable=no-value-for-parameter
