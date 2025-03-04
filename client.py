# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "grpcio",
#     "grpcio-tools",
#     "ipdb",
#     "inquirer",
#     "pillow",
# ]
# ///
"""
Script that starts a Image Transformer API service.
"""
import grpc
import logging
import inquirer
import io
from typing import Dict, Tuple
from PIL import Image
from pathlib import Path

from src import transformer_pb2_grpc
from src.image_transformer_servicer import OPERATION_REQUIRED_ARGS
from src.transformer_pb2 import TransformRequest, Operation, OperationType

SUPPORTED_EXTENSIONS = Image.registered_extensions()


def get_image_info() -> Tuple[str, bytes]:
    """
    Requests user for a support image and returns the image extension
    and bytes.
    """
    supported_extensions = ", ".join(SUPPORTED_EXTENSIONS)
    print(f"Supported Extensions: {supported_extensions}")
    questions = [
        inquirer.Path(
            "image",
            message=f"Which image would you like to tranform?",
            path_type=inquirer.Path.FILE,
        ),
    ]

    answers: Dict[str, str] = inquirer.prompt(questions)
    path = Path(answers["image"])
    if path.suffix in Image.EXTENSION.keys():
        image_path = answers["image"]
        with open(image_path, "rb") as f:
            return (path.suffix, f.read())
    else:
        return get_image_info()


def get_operations():
    """
    Requests the user to input operations they'd like to perform.
    """
    question = [
        inquirer.Text(
            "count",
            message="Enter the number of operations you'd like to perform",
            validate=lambda _, x: x.isdigit(),
        )
    ]

    count = int(inquirer.prompt(question)["count"])
    current = 1
    operations = []
    op_text_to_code = {
        "Rotate Left": OperationType.RotateLeft,
        "Rotate Right": OperationType.RotateRight,
        "Rotate N Degrees": OperationType.RotateN,
        "Flip Horizontally": OperationType.FlipHorizontally,
        "Flip Vertically": OperationType.FlipVertically,
        "Grayscale": OperationType.GrayScale,
        "Resize": OperationType.Resize,
        "Thumbnail": OperationType.Thumbnail,
    }

    while current <= count:
        question = [
            inquirer.List(
                "operation",
                message=f"Choose Operation No. {current}",
                choices=list(op_text_to_code.keys()),
            )
        ]
        answer = inquirer.prompt(question)["operation"]
        operation = op_text_to_code[answer]
        arguments = []

        # Request arguments:
        for field in OPERATION_REQUIRED_ARGS[operation]:
            question = [
                inquirer.Text(
                    field,
                    message=f"Enter {field}",
                    validate=lambda _, x: x.isdigit(),
                )
            ]
            arguments.append(int(inquirer.prompt(question)[field]))

        operations.append(Operation(kind=operation, arguments=arguments))
        current += 1
    return operations


def initialize(host: str, port: int):
    """
    Starts gRPC server
    """
    ext, image = get_image_info()
    operations = get_operations()
    with grpc.insecure_channel(f"{host}:{port}") as channel:
        stub = transformer_pb2_grpc.ImageTransformerStub(channel)
        try:
            response = stub.transform(
                TransformRequest(imageData=image, operation=operations)
            )
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                print(f"[ERROR] {e.details()}")
                exit(1)

    images = response.imageData
    images.extend(response.thumbnailData)
    answer = inquirer.prompt(
        [
            inquirer.Path(
                "location",
                message=f"Generated {len(images)} images. Where would you like to save them?",
            )
        ]
    )["location"]

    for i, image in enumerate(images):
        path = Path(answer) / f"{i}{ext}"
        im = Image.open(io.BytesIO(image))
        im.save(path, Image.EXTENSION[ext])


if __name__ == "__main__":
    logging.basicConfig()
    initialize(host="localhost", port=50051)
