from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError
try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.stdlib import StdlibIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    logging_integration = LoggingIntegration(level=None, event_level=None)
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=os.getenv("SENTRY_ENV", "development"),
        integrations=[logging_integration, StdlibIntegration(), StarletteIntegration()],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
        send_default_pii=True,
    )
except Exception:
    pass

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

s3 = boto3.client(
    's3',
    endpoint_url=os.getenv("S3_URL", "http://localstack:4566"),
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)

BUCKET_NAME = "stete-bucket"

@app.post("/upload-damage")
async def upload_damage(file: UploadFile = File(...)):
    try:
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="Neispravan file")

        s3.upload_fileobj(file.file, BUCKET_NAME, file.filename)

        return {"message": f"Slika {file.filename} poslana na obradu.", "status": "pending"}
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=502, detail=f"Greška pri uploadu na S3: {e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))