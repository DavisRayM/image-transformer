# Image Transformer API

[Swagger Docs](https://davisraym.com/image-transformer/)

An Image Processing RPC API plus an accompanying CLI tool that utilizes
the RPC API to perform image transformations.

The program can be used to batch various image transformation operations. *NOTE*: The operations are applied to the image in order

## Running the Project

This project utilizes Python with UV as the package manager. One can run
the package with [uv](https://docs.astral.sh/uv/) using the following
commands:

### Run Server

```sh
$ uv run server.py
```

### Run Client

```sh
$ uv run client.py
```

## Supported Transformation Operations

- Flipping: Horizontally and vertically
- Rotation: Rotate images by specified -/+n degrees, as well as a predefined rotate left and
rotate right.
- Grayscale conversion: Transform images to grayscale.
- Resizing: Adjust image dimensions to supplied dimensions.
- Thumbnail creation: Create a smaller 30x30 image.

## Supported Formats

The service supports a plethora of image formats, thanks to
[PIL](https://pillow.readthedocs.io). An comprehensive list of all
supported file formats can be found
[here](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).

## Design Pattern

The implementation of the API adheres to the Single Responsibility
Principle, ensuring that each function is designed to perform a single,
well-defined task i.e rotate_image only rotates an image.
