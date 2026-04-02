import grpc
from concurrent import futures
import gps_pb2
import gps_pb2_grpc
import traceback
import os
try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    logging_integration = LoggingIntegration(level=None, event_level=None)
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=os.getenv("SENTRY_ENV", "development"),
        integrations=[logging_integration],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
        send_default_pii=True,
    )
except Exception:
    pass

class GPSTrackerService(gps_pb2_grpc.GPSTrackerServicer):
    def SendLocation(self, request, context):
        try:
            print(f"[GPS] Vozilo {request.car_id} je na lokaciji: {request.latitude}, {request.longitude}")
            return gps_pb2.Empty()
        except Exception as e:
            print(f"[GPS][ERROR] {e}")
            traceback.print_exc()
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return gps_pb2.Empty()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gps_pb2_grpc.add_GPSTrackerServicer_to_server(GPSTrackerService(), server)
    server.add_insecure_port('[::]:50051')
    print("[*] gRPC GPS Server pokrenut na portu 50051...")
    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("[*] GPS server zaustavljen (KeyboardInterrupt)")
    except Exception as e:
        print(f"[*] GPS server error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    serve()