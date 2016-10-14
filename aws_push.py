#!/usr/bin/python
import boto3
import json
import argparse

def push_to_amazon_sns(title, body, targetArn, accessKey,
                       secretAccessKey, sound='default'):
    client = boto3.client('sns',
                          aws_access_key_id=accessKey,
                          aws_secret_access_key=secretAccessKey)
    
    aps =  { 'aps': { 'alert': {'title': title, 'body': body}, 'sound': sound } }
    msg = {
        'default': body,
        'APNS_SANDBOX': json.dumps(aps),
        'APNS': json.dumps(aps)    
    }

    client.publish(TargetArn=targetARN, Message=json.dumps(msg), MessageStructure='json')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Push to Amazon SNS.')
    parser.add_argument('--title',
                        help='the title for the APNS notification',
                        required=True)
    parser.add_argument('--body', 
                        help='the body of the notification',
                        required=True)
    parser.add_argument('--sound', 
                        help='the sound for the APNS notification ')
    parser.add_argument('--targetArn', 
                        help='the arn for the notification',
                        required=True)
    parser.add_argument('--access-key', 
                        help='the amazon access key',
                        required=True)
    parser.add_argument('--secret-access-key', 
                        help='the amazon secret access key',
                        required=True)

    args = parser.parse_args()

    push_to_amazon_sns(args.title, args.body, args.targetArn, args.access_key,
                       args.secret_access_key)
