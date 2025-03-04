"""
Servicer class implementation for the Image Transformer API
"""

import grpc
from PIL import Image
from io import BytesIO

from PIL.ImageFile import ImageFile
from src import transformer_pb2
from src.transformer_pb2 import TransformResponse, OperationType
from src import transformer_pb2_grpc

# 4000x4000 max image size
MAX_IMAGE_SIZE = (4000, 4000)

# Dimensions of a thumbail image
THUMBNAIL_DIMENSIONS = (30, 30)

# A map of the required arguments for each operation
OPERATION_REQUIRED_ARGS = {
    OperationType.RotateLeft: [],
    OperationType.RotateRight: [],
    OperationType.RotateN: ["Degrees"],
    OperationType.FlipHorizontally: [],
    OperationType.FlipVertically: [],
    OperationType.GrayScale: [],
    OperationType.Resize: ["Width", "Height"],
    OperationType.Thumbnail: [],
}


class ImageTransformerServicer(transformer_pb2_grpc.ImageTransformerServicer):
    """
    Servicer Implementation for the ImageTransformer API
    """

    def validate_image(self, request, context):
        """
        Validate image size and constraints
        """
        im = Image.open(BytesIO(request.imageData))
        width, height = im.size
        MAX_WIDTH, MAX_HEIGHT = MAX_IMAGE_SIZE
        if width > MAX_WIDTH or height > MAX_HEIGHT:
            self.set_error(
                context,
                f"Invalid image: Image should have a maximum of {MAX_IMAGE_SIZE[0]}x{MAX_IMAGE_SIZE[1]} pixels",
            )

    def validate_operations(self, request, context):
        """
        Validates the requested image operations; ensures required arguments
        are present.
        """
        for op in request.operation:
            required = OPERATION_REQUIRED_ARGS[op.kind]
            if len(required) != len(op.arguments):
                args = ", ".join(required)
                name = transformer_pb2._OPERATIONTYPE.values_by_number[op.kind].name
                self.set_error(
                    context,
                    f"Invalid operation; {name} requires {len(required)} arguments: {args}",
                )

    def resize_image(self, image: ImageFile, width: int, height: int) -> ImageFile:
        """
        Resize an image to fit the specified width & height
        """
        return image.resize((width, height))

    def rotate_image(self, image: ImageFile, degrees: int) -> ImageFile:
        """
        Rotate Image by `degrees` and return rotated image
        """
        return image.rotate(degrees)

    def grayscale_image(self, image: ImageFile) -> ImageFile:
        """
        Grayscales an image
        """
        return image.convert("L")

    def flip_image(self, image: ImageFile, horizontal: bool) -> ImageFile:
        """
        Flips an image horizontally if `horizontal` is true otherwise
        switches it vertically.
        """
        return image.transpose(
            Image.Transpose.FLIP_LEFT_RIGHT
            if horizontal
            else Image.Transpose.FLIP_TOP_BOTTOM
        )

    def set_error(self, context, message):
        """
        Sets the request error and returns error response
        """
        context.abort(grpc.StatusCode.INVALID_ARGUMENT, message)

    def perform_operations(self, request):
        """
        Performs the requested operations on the image. Returning the latest
        version of the image after operation alongside requested thumbnails.
        """
        im = Image.open(BytesIO(request.imageData))
        format = im.format
        thumbnails = []

        for op in request.operation:
            match op.kind:
                case OperationType.RotateLeft:
                    im = self.rotate_image(im, -90)
                case OperationType.RotateRight:
                    im = self.rotate_image(im, 90)
                case OperationType.RotateN:
                    im = self.rotate_image(im, op.arguments[0])
                case OperationType.FlipHorizontally:
                    im = self.flip_image(im, horizontal=True)
                case OperationType.FlipVertically:
                    im = self.flip_image(im, horizontal=False)
                case OperationType.GrayScale:
                    im = self.grayscale_image(im)
                case OperationType.Resize:
                    im = self.resize_image(im, op.arguments[0], op.arguments[1])
                case OperationType.Thumbnail:
                    ret_image = BytesIO()
                    self.resize_image(
                        im, THUMBNAIL_DIMENSIONS[0], THUMBNAIL_DIMENSIONS[1]
                    ).save(ret_image, format)
                    thumbnails.append(ret_image.getvalue())

        ret_image = BytesIO()
        im.save(ret_image, format)

        return TransformResponse(
            imageData=[ret_image.getvalue()], thumbnailData=thumbnails
        )

    def transform(self, request, context):
        """
        Handles transform requests from the client.
        """
        # Check if image is valid
        self.validate_image(request, context)
        # Check if required operation data has been passed
        self.validate_operations(request, context)
        # Perform operations on the image and return response
        return self.perform_operations(request)
