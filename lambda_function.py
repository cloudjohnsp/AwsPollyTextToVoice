import json
import boto3
import os
import uuid

polly_client = boto3.client('polly')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # Parse the JSON request
        body = json.loads(event['body'])
        text = body['text']
        bucket_name = os.environ['BUCKET_NAME']
        object_key = f"{uuid.uuid4()}.mp3"

        # Convert text to speech using Amazon Polly
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna'
        )

        # Save the audio stream to S3
        if 'AudioStream' in response:
            with response['AudioStream'] as stream:
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=object_key,
                    Body=stream.read(),
                    ContentType='audio/mpeg'
                )

        # Return a success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Text has been converted to speech and saved to S3.',
                's3_key': object_key
            })
        }
    except Exception as e:
        # Return an error response
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
