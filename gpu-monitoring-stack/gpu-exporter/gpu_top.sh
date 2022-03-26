#/bin/bash

while true; do
    nvidia-smi --query-gpu="gpu_name,uuid,index" --format=csv,noheader > gpu_info
    nvidia-smi --query-compute-apps="gpu_uuid,pid,process_name,used_memory" --format=csv,noheader > gpu_ps_mem
    
    python3 gpu_ps.py
    sleep 1
done

