#!/usr/bin/env python
from email import header
import sys
from urllib import response
import requests
import docker
import paramiko

def monitors():
    targetURL = "http://localhost:9091"
    response = requests.get(targetURL + '/api/v1/query?query=DCGM_FI_DEV_SM_CLOCK')
    res_json = response.json()
    print(f"GPU ModelName = {res_json['data']['result'][0]['metric']['modelName']}")
    print(f"Instance = {res_json['data']['result'][0]['metric']['instance']}")
        
    print(f"Current GPU Clock = {res_json['data']['result'][0]['value'][1]} MHz")

    response = requests.get(targetURL + '/api/v1/query?query=DCGM_FI_DEV_GPU_UTIL')
    res_json = response.json()
    print(f"Current GPU Utilization = {res_json['data']['result'][0]['value'][1]} %")

    response = requests.get(targetURL + '/api/v1/query?query=DCGM_FI_DEV_FB_FREE')
    res_json = response.json()
    print(f"Current GPU Memory (Free) = {res_json['data']['result'][0]['value'][1]} MiB")

def start(Environments, ContainerName):
    portainerURL = "https://localhost:9443/api/endpoints"
    postURL = f"{portainerURL}/{Environments}/docker/containers/{ContainerName}/start"
    response = requests.post(postURL, verify=False, headers={"X-API-Key": 'portainer api-key'})
    print(response)
    print(response.headers)

def create(Environments, ContainerName, Image, VolumeBind, FileName, Tag="latest"):
    portainerURL = "https://localhost:9443/api/endpoints"
    postURL = f"{portainerURL}/{Environments}/docker/containers/create?name={ContainerName}"

    data = {
        "HostConfig": {
            "Binds": [
                f"{VolumeBind}:/tmp"
            ],
            "DeviceRequests": [
                {
                    "Count": -1,
                    "Capabilities": [
                        [
                            "gpu"
                        ]
                    ]
                }
            ]
        },
        "Cmd": [
            "python",
            f"{FileName}"
        ],
        "Image": f"{Image}:{Tag}"
    }
    print(postURL)
    print(data)

    response = requests.post(postURL, verify=False, headers={"X-API-Key": 'portainer api-key'}, json=data)

    print(response)
    print(response.headers)

def check(RequestedMemory):
    targetURL = "http://localhost:9091"
    response = requests.get(targetURL + '/api/v1/query?query=DCGM_FI_DEV_FB_FREE')
    res_json = response.json()
    freeMemory = int(res_json['data']['result'][0]['value'][1])
    print(f"Current GPU Memory (Free) = {res_json['data']['result'][0]['value'][1]} MiB")
    if freeMemory - (RequestedMemory + 768) > 512 :
        return True
    return False

def line_prepender(filename, line):
    new_file = filename.rstrip(".py") + "_gpu.py"
    with open(new_file, "w+") as fn:
        with open(filename, 'r+') as f:
            content = f.read()
            fn.seek(0, 0)
            fn.write(line.rstrip('\r\n') + '\n' + content)
    return new_file

def createSSHClient(server, port, user):
    key = paramiko.Ed25519Key.from_private_key_file("/home/your_username/.ssh/paramiko_gpu")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, pkey = key)
    return client

def copyFile(pathHost, pathDes="/tmp/file"):
    ssh = createSSHClient("gpu.localhost", 22, "your_username")
    sftp = ssh.open_sftp()
    
    sftp.put(pathHost, pathDes)
    
    sftp.close()
    ssh.close()


def line_appender(filename, line):
    with open(filename, "a+") as fn:
        fn.write(line)
    return filename

if __name__ == "__main__":
    print(f"Arguments count: {len(sys.argv)}")

    containerName = input("Enter ContainerName: ")
    print(containerName)
    
    # imageName = input("Enter ImageName: ")
    imageName = "tensorflow/tensorflow"
    print(imageName)

    # tagName = input("Enter ImageTag: ")
    # print(tagName)
    # if check(1024):
    #     create(2, containerName, imageName, 8888, 9998, Tag=tagName)
    #     start(2, containerName)
    # else:
    #     print("Cannot start the workload: Not Enough Memory")
    
    # locate file
    # ask memory
    # check memory availability
    # inject script
    # upload via scp
    # docker run -it --rm -d -v /path/to/python/file/dir:/tmp -w /tmp tensorflow/tensorflow python file_name.py

    python_src = input("Enter python script/code location: ")

    gpu_memory = input("How much memory do you need? ")

    if check(int(gpu_memory)):
        gpu_declaration = f"""import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
if gpus:
# Restrict TensorFlow to only allocate 1GB of memory on the first GPU
    try:
        tf.config.set_logical_device_configuration(
            gpus[0],
            [tf.config.LogicalDeviceConfiguration(memory_limit={gpu_memory})])
        logical_gpus = tf.config.list_logical_devices('GPU')
        print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        # Virtual devices must be set before GPUs have been initialized
        print(e)"""

        python_src_gpu = line_prepender(python_src, gpu_declaration)

        model_saving = """
    import time
    import sys
    
    filepath = f"{sys.argv[0].rstrip('.py')}"
    filepath = f"{filepath.lstrip('/tmp')}"
    filename = f"{filepath}-{int(time.time())}.h5"
    model.save(f'{filename}')
    
    from minio import Minio
    client = Minio("172.17.0.1:9000", "[MINIO ACCESS KEY]", "[MINIO SECRET]", secure=False)
    res = client.fput_object("model-bucket", f"{filename}", f"{filename}")
    print(
        "created {0} object; etag: {1}, version-id: {2}".format(
            res.object_name, res.etag, res.version_id,
        ),
    )
"""
        python_src_gpu = line_appender(python_src_gpu, model_saving)
        print(python_src_gpu)
        copyFile(python_src_gpu, "/tmp/" + python_src_gpu.split("/")[-1])
        create(2, containerName, "tensorflow/tensorflow", "/tmp", "/tmp/" + python_src_gpu.split("/")[-1], Tag="latest-gpu")
        start(2, containerName)
    else:
        print("Cannot start the workload: Not Enough Memory")

