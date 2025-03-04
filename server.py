# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "grpcio",
#     "grpcio-tools",
#     "pillow",
#     "ipdb",
# ]
# ///
"""
Script that starts a Image Transformer API service.
"""
from concurrent import futures
import grpc
import logging

from src import transformer_pb2_grpc
from src.image_transformer_servicer import ImageTransformerServicer


def initialize(port: int):
    """
    Starts gRPC server
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    transformer_pb2_grpc.add_ImageTransformerServicer_to_server(
        ImageTransformerServicer(), server
    )
    server.add_insecure_port("[::]:" + str(port))
    server.start()
    print(f"Server started, listening on {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    initialize(port=50051)
