from __future__ import print_function

import boto3
from decimal import Decimal
import json
import urllib
from datetime import datetime
import re
import unicodedata
print('Loading function')

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
sns = boto3.client('sns')
rekognition = boto3.client('rekognition')
    
# --------------- Helper Functions ------------------

def update_db(table_name, totem_id, rekognition_time, deeplens_id, s3_bucket, s3_key):
    response = dynamodb.put_item(
        TableName=table_name,
        Item={
            'totem_id': {'S': totem_id},
            'rekognition_time': {'S': rekognition_time},
            'deeplens_id': {'S': deeplens_id},
            's3_bucket': {'S': s3_bucket},
            's3_key': {'S': s3_key}
            }
        ) 


def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3 
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)

def text_to_id(text):
    text = strip_accents(text.lower())
    text = re.sub('[ ]+', '_', text)
    text = re.sub('[^0-9a-zA-Z_-]', '', text)
    return text
    
# --------------- Main handler ------------------

def lambda_handler(event, context):

    # number = '+16262263799'  
    #sns.publish(PhoneNumber = number, Message='Detected a face!' )
    
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(
        event['Records'][0]['s3']['object']['key'].encode('utf8'))

    try:

        # Calls Amazon Rekognition Search Face API to compare the face detected 
        # in the 'djs' index
        '''
        result = rekognition.search_faces_by_image(
            CollectionId="djs",
            Image={ 'S3Object':{
                'Bucket': bucket,
                'Name': key
                } 
            },
            MaxFaces=1
        )
        '''

        result = rekognition.recognize_celebrities(
            Image={ "S3Object": {
                "Bucket": bucket,
                "Name": key,
                }
            },
        )

        if result['CelebrityFaces']:
            
            print('Found a matching celebrity!')
            #totem_id = result['FaceMatches'][0]['Face']['ExternalImageId']
            #prob = result['FaceMatches'][0]['Similarity']
            totem_name = result['CelebrityFaces'][0]['Name']
            totem_id = text_to_id(totem_name)
            prob = result['CelebrityFaces'][0]['MatchConfidence']
            
            #sns.publish(PhoneNumber = number, Message= externalid )
            
            # See if the faceID exists in the DynamoDB already
            response = dynamodb.query(TableName='totem_location',
                            Select='ALL_ATTRIBUTES',
                            KeyConditionExpression='totem_id = :x',
                            ExpressionAttributeValues={':x' : {'S' : totem_id}},
                            ScanIndexForward=False,
                            Limit=1)
            update_flag = 0
            
            if response['Items']: #key exist already
                print('Found an existing key in DynamoDB!')
                item_timestamp = datetime.strptime(response['Items'][0]['rekognition_time']['S'], '%Y-%m-%d %H:%M:%S')
                rekognition_time = datetime.strptime(result['ResponseMetadata']['HTTPHeaders']['date'], '%a, %d %b %Y %H:%M:%S %Z')
                # only update the DB if at least 1 min has passed since last detected
                print('Total Time Difference: '+str((rekognition_time-item_timestamp).total_seconds()))
                if (rekognition_time-item_timestamp).total_seconds() > 60: 
                    update_flag = 1
            else:
                print('New DJ detected!')
                update_flag = 1
            
            if (update_flag == 1):
                #update the database with totem_id and the time detected
                print('Adding entry to DynamoDB')
                table_name = 'totem_location'
                rekognition_time = datetime.strptime(result['ResponseMetadata']['HTTPHeaders']['date'], '%a, %d %b %Y %H:%M:%S %Z')
                rekognition_time_formatted = rekognition_time.strftime('%Y-%m-%d %H:%M:%S')
                deeplens_id = key.split('-image-')[0]
                update_db(table_name, totem_id, rekognition_time_formatted, deeplens_id, bucket, key)
                
                msg = "Positive match identified with {:.3f}% similarity to ".format(prob)
                msg += 'DJ {}.'.format(totem_id)
                
                #Send a text message to alert the user of the match 
                #number = '+16262263799'  
                # sns.publish(PhoneNumber = number, Message=msg )
            
        else:
                print("No match is found.")

    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket))
        raise e