# Running tensorflow with GPU support and Jupyter

```bash
docker run --gpus all -d -p 9999:8888 tensorflow/tensorflow:latest-gpu-jupyter

python cnn_benchmark.py
```

Modify this part to limit GPU memory allocated to the ML process, according to your own specification.

```py
...
  try:
    tf.config.set_logical_device_configuration(
        gpus[0],
        [tf.config.LogicalDeviceConfiguration(memory_limit=1024)]) # this part
    logical_gpus = tf.config.list_logical_devices('GPU')
...
```
# Readings and Resources

1. https://www.tensorflow.org/install/docker
2. https://www.tensorflow.org/guide/gpu
3. https://www.milindsoorya.com/blog/handwritten-digits-classification
4. https://machinelearningmastery.com/how-to-develop-a-convolutionalneural-network-from-scratch-for-mnist-handwritten-digit-classification/
5. https://www.analyticsvidhya.com/blog/2021/11/benchmarking-cpuand-gpu-performance-with-tensorflow/
6. https://medium.com/@andriylazorenko/tensorflow-performance-testcpu-vs-gpu-79fcd39170c
7. http://pe-kay.blogspot.com/2017/05/how-to-change-resource-limit-ofrunning.html
8. https://www.baeldung.com/ops/docker-memory-limit