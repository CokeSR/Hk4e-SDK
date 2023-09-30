import os
import subprocess

# 绝对路径
protoc_path = "C:/Users/15008/Desktop/GitHub/Hk4e-SDKSever-Py/protobuild/srv/bin/protoc.exe"
proto_folder_path = "C:/Users/15008/Desktop/GitHub/Hk4e-SDKSever-Py/protobuild/proto"
output_folder_path = "C:/Users/15008/Desktop/GitHub/Hk4e-SDKSever-Py/data/proto"

def convert_proto_to_python(proto_folder, output_folder, protoc_path):
    for root, dirs, files in os.walk(proto_folder):
        for file in files:
            if file.endswith(".proto"):
                proto_path = os.path.join(root, file)
                output_file = file.replace(".proto", "_pb2.py")
                output_path = os.path.join(output_folder, output_file)
                command = f"{protoc_path} --python_out={output_folder} --proto_path={proto_folder} {proto_path}"
                subprocess.call(command, shell=True)
convert_proto_to_python(proto_folder_path, output_folder_path, protoc_path)