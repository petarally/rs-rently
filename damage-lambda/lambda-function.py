import json

def handler(event, context):
    try:
        records = event.get('Records', [])
        if not records:
            return {'statusCode': 400, 'body': json.dumps('Nema zapisa u eventu')}

        for record in records:
            try:
                bucket = record['s3']['bucket']['name']
                key = record['s3']['object']['key']

                print(f"[LAMBDA] Detektirana nova slika štete!")
                print(f"[LAMBDA] Obrađujem datoteku {key} iz bucketa {bucket}...")
            except KeyError as ke:
                print(f"[LAMBDA] Preskočen zapis zbog nedostajućeg polja: {ke}")
                continue

        return {
            'statusCode': 200,
            'body': json.dumps('Obrada uspješna!')
        }
    except Exception as e:
        print(f"[LAMBDA][ERROR] {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Greška pri obradi: {e}')
        }