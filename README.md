## 1. Start TF2 object detection service

```commandline
cd tfserve
docker build -t s2d-detection .
docker run -p 8501:8501 s2d-detection
```
The `model` folder contains versioned model weights that are exported post-training. The TensorFlow Serving official Docker image (`tensorflow/serving`) is utilized to serve the s2d object detection model. Once the container is built and started, the model becomes accessible through both `gRPC` and `REST` protocols.

If the service is launched successfully, you should see the following messages:


```commandline
...
2024-01-17 20:47:00.893640: I tensorflow_serving/core/loader_harness.cc:95] Successfully loaded servable version {name: s2d version: 1}
2024-01-17 20:47:00.895907: I tensorflow_serving/model_servers/server_core.cc:488] Finished adding/updating models
2024-01-17 20:47:00.895986: I tensorflow_serving/model_servers/server.cc:118] Using InsecureServerCredentials
2024-01-17 20:47:00.896001: I tensorflow_serving/model_servers/server.cc:383] Profiler service is enabled
2024-01-17 20:47:00.897285: I tensorflow_serving/model_servers/server.cc:409] Running gRPC ModelServer at 0.0.0.0:8500 ...
[warn] getaddrinfo: address family for nodename not supported
[evhttp_server.cc : 245] NET_LOG: Entering the event loop ...
2024-01-17 20:47:00.902848: I tensorflow_serving/model_servers/server.cc:430] Exporting HTTP/REST API at:localhost:8501 ...
...
```

## 2. Install tesseract-ocr

### MacOS

```commandline
brew install tesseract
```



