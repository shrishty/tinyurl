import json
import boto3
import os
import datetime
import uuid
import random
import string

from typing import Any, Dict

URL_TABLE_NAME = os.getenv('URL_TABLE_NAME')
BASE_URL = os.getenv('BASE_URL')
dynamodb = boto3.resource('dynamodb')
url_table = dynamodb.Table(URL_TABLE_NAME)

def create_short_url(event: Dict[str, Any], context) -> Dict[str, Any]:
    print(event)
    request_body = json.loads(event['body'])
    long_url = request_body['longUrl']
    id = str(uuid.uuid4())
    short_id = ''.join(random.choices(string.ascii_lowercase, k=5))
    short_url = f'{BASE_URL}/tinyurl/{short_id}'
    creation_time = datetime.datetime.now()
    ttl = (creation_time + datetime.timedelta(days=7)).timestamp()

    url_table.put_item(
        Item={
            'PK': short_id,
            'SK': short_id,
            'longUrl': long_url,
            'shortUrl': short_url,
            'creationTime': str(creation_time.isoformat()),
            'ttl': int(ttl)
        }
    )
    body = {
        "baseUrl": BASE_URL,
        "shortUrl": short_url,
        "longUrl": long_url,
        "expirationTimeIso": str(creation_time.isoformat())
    }

    print(f"the response body is: {body}")

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

def get_long_url(event: Dict[str, Any], context) -> Dict[str, Any]:
    short_id = event['pathParameters']['id']
    response = url_table.get_item(
        Key={
            'PK': short_id,
            'SK': short_id,
        }
    )
    item = response.get('Item', {})
    return {
        "statusCode": 302,
        "headers": {
            "Location": item['longUrl']
        },
        "body": json.dumps({
            'longUrl': item['longUrl'],
            'shortUrl': item['shortUrl'],
            'creationTime': item['creationTime'],
            'ttl': int(item['ttl'])
        })
    }