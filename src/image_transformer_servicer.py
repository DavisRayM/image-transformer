"""
Server class implementation for the Image Transformer API
"""
from src import transformer_pb2
from src import transformer_pb2_grpc


class ImageTransformerServicer(transformer_pb2_grpc.ImageTransformerServicer):
    """
    Servicer Implementation for the ImageTransformer API
    """

    def transform(self, request, context):
        """
        Handles transform requests from the client.
        """
        return transformer_pb2.TransformResponse(imageData=["test"], thumbnailData=["test"])
