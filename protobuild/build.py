import os
import subprocess

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
proto_folder = os.path.join(script_dir, "proto", "cbt")
output_folder = os.path.join(script_dir, "output")
protoc = os.path.join(script_dir, "srv", "bin", "protoc.exe")

def convert_proto_to_python(proto_folder, output_folder, protoc):
    for root, dirs, files in os.walk(proto_folder):
        for file in files:
            if file.endswith(".proto"):
                proto = os.path.join(root, file)
                output_file = file.replace(".proto", "_pb2.py")
                output = os.path.join(output_folder, output_file)
                command = [protoc, f"--python_out={output_folder}", f"--proto={proto_folder}", proto]
                subprocess.run(command, shell=True, check=True)

if __name__ == "__main__":
    convert_proto_to_python(proto_folder, output_folder, protoc)
