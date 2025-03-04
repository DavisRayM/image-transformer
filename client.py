# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "grpcio",
#     "grpcio-tools",
#     "ipdb",
# ]
# ///
"""
Script that starts a Image Transformer API service.
"""
from concurrent import futures
import grpc
import logging

from src import transformer_pb2_grpc, transformer_pb2
from src.image_transformer_servicer import ImageTransformerServicer

def initialize(host: str, port: int):
    """
    Starts gRPC server
    """
    with grpc.insecure_channel(f"{host}:{port}") as channel:
        stub = transformer_pb2_grpc.ImageTransformerStub(channel)
        response = stub.transform(transformer_pb2.TransformRequest(imageData="", operation=[]))
    print(f"client received {response.imageData} - {response.thumbnailData}")


if __name__ == "__main__":
    logging.basicConfig()
    initialize(host="localhost", port=50051)
