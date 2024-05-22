import boto3
import botocore.config
import json

from datetime import datetime


def Newsletter_generate_using_bedrock(Newslettertopic: str) -> str:
    prompt = f"""<s>[INST]Human: Write a 200 words blog on the topic {Newslettertopic}
    Assistant:[/INST]
    """

    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9
    }

    try:
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1",
                               config=botocore.config.Config(read_timeout=300, retries={'max_attempts': 3}))
        response = bedrock.invoke_model(body=json.dumps(body), modelId="meta.llama3-8b-instruct-v1:0")

        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        print(response_data)
        newsletter_details = response_data['generation']
        return newsletter_details
    except Exception as e:
        print(f"Error generating the newsletter:{e}")
        return ""


def save_newsletter_details_s3(s3_key, s3_bucket, generate_newsletter):
    s3 = boto3.client('s3')

    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_newsletter)
        print("Code saved to s3")

    except Exception as e:
        print("Error when saving the code to s3")


def lambda_handler(event, context):
    # TODO implement
    event = json.loads(event['body'])
    newslettertopic = event['newsletter_topic']

    generate_newsletter = newsletter_generate_using_bedrock(newslettertopic=newslettertopic)

    if generate_newsletter:
        current_time = datetime.now().strftime('%H%M%S')
        s3_key = f"newsletter-output/{current_time}.txt"
        s3_bucket = 'aws_bedrock_1'
        save_newsletter_details_s3(s3_key, s3_bucket, generate_newsletter)


    else:
        print("No newsletter was generated")

    return {
        'statusCode': 200,
        'body': json.dumps('Newsletter Generation is completed')
    }





