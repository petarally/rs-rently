import grpc
from concurrent import futures
import gps_pb2
import gps_pb2_grpc

class GPSTrackerService(gps_pb2_grpc.GPSTrackerServicer):
    def SendLocation(self, request, context):
        print(f"[GPS] Vozilo {request.car_id} je na lokaciji: {request.latitude}, {request.longitude}")
        return gps_pb2.Empty()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gps_pb2_grpc.add_GPSTrackerServicer_to_server(GPSTrackerService(), server)
    server.add_insecure_port('[::]:50051')
    print("[*] gRPC GPS Server pokrenut na portu 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()