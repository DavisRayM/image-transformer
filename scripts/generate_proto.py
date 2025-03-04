# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "grpcio",
#     "grpcio-tools",
# ]
# ///
"""
Automated script for generating/updating the protobuf definitions used
by the application.

Run using: uv run scripts/generate_proto.py
"""
import os
import glob
import grpc_tools.protoc

SOURCE_DIR = "protos"
OUTPUT_DIR = "src"

def generate_protobufs():
    """
    Generates python gRPC and Protobuf files from .proto definitions.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    proto_files = glob.glob(os.path.join(SOURCE_DIR, "*.proto"))
    if not proto_files:
        print(f"No .proto files found in: {SOURCE_DIR}")
        return

    for proto_file in proto_files:
        command = [
            "grpc_tools.protoc",
            f"--proto_path={SOURCE_DIR}",
            f"--python_out={OUTPUT_DIR}",
            f"--grpc_python_out={OUTPUT_DIR}",
            proto_file
        ]
        grpc_tools.protoc.main(command)
    print(f"Protobufs generated successfully in: {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_protobufs()
