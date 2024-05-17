import boto3
import json
import base64
from botocore.exceptions import ClientError

def send_sns_alert(message):
    sns_client = boto3.client('sns')
    sns_client.publish(
        TopicArn='arn:aws:sns:us-east-1:<id>:UnauthorizedAccessAlerts',
        Message=message,
        Subject='Security Alert: Unauthorized Access Attempt'
    )

def query_patient_details(external_image_id):
    dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
    print(f"Querying for patient details with ID: {external_image_id}")
    try:
        response = dynamodb_client.get_item(
            TableName='patients',
            Key={'patient_id': {'S': external_image_id}}
        )
        print("DynamoDB response for patient details:", response)
        if 'Item' in response:
            item = response['Item']
            return {k: v.get('S', v.get('N', '')) for k, v in item.items()}
        else:
            print("No patient details found for ID:", external_image_id)
            return {}
    except ClientError as e:
        print(f"Error querying DynamoDB for patient details: {str(e)}")
        return None

def query_visits_details(external_image_id):
    dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
    print(f"Querying for visits related to external_image_id: {external_image_id}")
    try:
        response = dynamodb_client.query(
            TableName='visits',
            IndexName='patient_id-index',
            KeyConditionExpression='patient_id = :pid',
            ExpressionAttributeValues={':pid': {'S': external_image_id}}
        )
        print("DynamoDB response for visits details:", response)
        return [dict((k, v.get('S', v.get('N', ''))) for k, v in item.items()) for item in response.get('Items', [])]
    except ClientError as e:
        print(f"Error querying DynamoDB for visits: {str(e)}")
        return []

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    s3_client = boto3.client('s3')
    rekognition_client = boto3.client('rekognition')

    if 'Records' in event:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
    elif 'body' in event:
        base64_image = json.loads(event['body'])['image']
        image_data = base64.b64decode(base64_image.split(",")[-1])
        bucket = 'suprith-face-security-system'
        key = 'known-faces/' + context.aws_request_id + '.jpg'
        s3_client.put_object(Bucket=bucket, Key=key, Body=image_data)
    else:
        print("Invalid event format")
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps("Bad Request: Event format incorrect.")
        }

    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()
    except Exception as e:
        print("Failed to retrieve image from S3:", e)
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps("Failed to retrieve image from S3.")
        }

    try:
        detect_response = rekognition_client.detect_faces(
            Image={'Bytes': image_data},
            Attributes=['ALL']
        )
        if not detect_response['FaceDetails']:
            send_sns_alert("No faces detected in the image.")
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps("Alert : No faces detected.")
            }

        search_response = rekognition_client.search_faces_by_image(
            CollectionId='known-faces',
            Image={'Bytes': image_data},
            MaxFaces=1,
            FaceMatchThreshold=85
        )
        if not search_response['FaceMatches']:
            send_sns_alert("No Face Matched with Records. New Patient .")
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps("Alert : No matching face found.")
            }

        matched_face = search_response['FaceMatches'][0]['Face']
        external_image_id = matched_face.get('ExternalImageId', 'Unknown Person')
        print("Matched external image ID:", external_image_id)

        patient_details = query_patient_details(external_image_id)
        visits_details = query_visits_details(external_image_id)

        if patient_details:
            print("Patient details found for ID:", external_image_id)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    "message": f"Welcome {patient_details['name']}! Patient Details Found.",
                    "patient_info": patient_details,
                    "visits": visits_details
                })
            }
        else:
            print("Patient details not found for ID:", external_image_id)
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps("Alert : Patient details not found.")
            }
    except Exception as e:
        print(f"Error processing faces: {str(e)}")
        return {
            'statusCode': 403,
            'headers': headers,
            'body': json.dumps(f"Failed to process faces. Please try again with different format")
        }
