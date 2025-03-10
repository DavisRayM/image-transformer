import grpc
import grpc_testing
import unittest

from src import transformer_pb2
from src.image_transformer_servicer import ImageTransformerServicer


class TestImageTransformer(unittest.TestCase):
    def setUp(self):
        servicers = {
            transformer_pb2.DESCRIPTOR.services_by_name[
                "ImageTransformer"
            ]: ImageTransformerServicer()
        }
        self.test_server = grpc_testing.server_from_dictionary(
            servicers, grpc_testing.strict_real_time()
        )

    def test_missing_arguments(self):
        """Expect an error if required arguments are missing"""
        with open("tests/test.jpg", "rb") as f:
            image = f.read()
        operations = [
            transformer_pb2.Operation(
                kind=transformer_pb2.OperationType.RotateN, arguments=[]
            )
        ]
        req = transformer_pb2.TransformRequest(imageData=image, operation=operations)
        transform_method = self.test_server.invoke_unary_unary(
            method_descriptor=(
                transformer_pb2.DESCRIPTOR.services_by_name[
                    "ImageTransformer"
                ].methods_by_name["transform"]
            ),
            invocation_metadata={},
            request=req,
            timeout=1,
        )

        response, metadata, code, details = transform_method.termination()
        self.assertEqual(code, grpc.StatusCode.INVALID_ARGUMENT)
        self.assertEqual(
            details, "Invalid operation; RotateN requires 1 arguments: Degrees"
        )


if __name__ == "__main__":
    unittest.main()
