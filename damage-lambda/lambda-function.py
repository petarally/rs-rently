import json

def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        print(f"[LAMBDA] Detektirana nova slika štete!")
        print(f"[LAMBDA] Obrađujem datoteku {key} iz bucketa {bucket}...")
        
    return {
        'statusCode': 200,
        'body': json.dumps('Obrada uspješna!')
    }