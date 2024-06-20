import json
import boto3
import os
import uuid

polly_client = boto3.client("polly")
s3_client = boto3.client("s3")


def lambda_handler(event, context):
    try:
        # Get bucket name
        bucket_name = os.environ["BUCKET_NAME"]

        # Parse the JSON request for text-to-speech operation
        body = json.loads(event["body"])
        text = body.get("text")

        if not text:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                },
                "body": json.dumps({"error": "Missing text in request body"}),
            }

        object_key = f"{uuid.uuid4()}.mp3"

        # Convert text to speech using Amazon Polly
        response = polly_client.synthesize_speech(
            Text=text, OutputFormat="mp3", VoiceId="Joanna"
        )

        # Save the audio stream to S3
        if "AudioStream" in response:
            with response["AudioStream"] as stream:
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=object_key,
                    Body=stream.read(),
                    ContentType="audio/mpeg",
                )

        # Generate a pre-signed URL for the audio file
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=3600,
        )

        # Return a success response
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps(
                {
                    "message": "Text has been converted to speech and saved to S3.",
                    "s3_key": object_key,
                    "presigned_url": presigned_url,
                }
            ),
        }

    except Exception as e:
        # Return an error response
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps({"error": str(e)}),
        }
