FROM ubuntu:focal

COPY gpu_top.sh gpu_ps.py ./
RUN apt-get update && apt-get install -y \
        python3 python3-pip

RUN pip install requests

ENTRYPOINT ["/bin/bash", "gpu_top.sh"]

