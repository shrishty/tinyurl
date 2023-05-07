import json
import boto3
import shortuuid
import os
import datetime
from typing import Any, Dict

URL_TABLE_NAME = os.getenv('URL_TABLE_NAME')
BASE_URL = os.getenv('BASE_URL')
dynamodb = boto3.resource('dynamodb')
url_table = dynamodb.Table(URL_TABLE_NAME)

def create_short_url(event: Dict[str, Any], context) -> Dict[str, Any]:
    request_body = json.loads(event['body'])
    long_url = request_body['longUrl']
    id = shortuuid.uuid()
    short_url = shortuuid.uuid()[0:7]
    creation_time = datetime.datetime.now()
    ttl = (creation_time + datetime.timedelta(days=7)).timestamp()

    url_table.put_item(
        Item={
            'id': id,
            'longUrl': long_url,
            'shortUrl': short_url,
            'creationTime': creation_time,
            'ttl': ttl
        }
    )
    body = {
        "baseUrl": BASE_URL,
        "shortUrl": short_url,
        "longUrl": long_url,
        "expirationTimeIso": creation_time.isoformat()
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

def get_long_url(event: Dict[str, Any], context) -> Dict[str, Any]:
    return {
        "statusCode": 302,
        "headers": {
            "Location": "https://www.google.com"
        },
        "body": json.dumps({
            'event': event
        })
    }