#!/usr/bin/env python3
import requests

gpu_info = open("gpu_info", "r")
gpu_dictionary = {}
while True:
    line = gpu_info.readline()
    if not line:
        break
    gpu_info_parsed = line.rstrip("\n").split(", ")
    gpu_dictionary[gpu_info_parsed[1]] = [gpu_info_parsed[0], gpu_info_parsed[2]]

gpu_info.close()

gpu_ps = open("gpu_ps_mem", "r")
gpu_ps_list = []
while True:
    line = gpu_ps.readline()
    if not line:
        break
    gpu_info_parsed = line.rstrip("\n").split(", ")
    gpu_ps_list.append(gpu_dictionary[gpu_info_parsed[0]] + gpu_info_parsed)

gpu_ps.close()

nvidia_gpu_process = "# HELP nvidia_process Process Info\n"
nvidia_gpu_process += "# TYPE nvidia_process gauge\n"

for ps_info in gpu_ps_list:
    nvidia_gpu_process += f"""nvidia_process{{{f'gpu="{ps_info[1]}",UUID="{ps_info[2]}",modelName="{ps_info[0]}",process="{ps_info[4]}",pid="{ps_info[3]}"'}}} {ps_info[5][:-4]}\n"""

print(nvidia_gpu_process)

res = requests.post("http://172.17.0.1:9081/metrics/job/nvidia_gpu_process", data=nvidia_gpu_process, headers={"Content-Type":"text/plain"})

print(res.text)

