# s2d


## 1. Start s2d object detection service

```commandline
cd tfserve
docker build -t s2d-detection .
docker run -p 8501:8501 s2d-detection
```

If the service was launched successfully, the following messages should be visible:

```commandline
...
2024-01-17 20:46:59.383123: I tensorflow_serving/model_servers/server_core.cc:467] Adding/updating models.
2024-01-17 20:46:59.383157: I tensorflow_serving/model_servers/server_core.cc:596]  (Re-)adding model: s2d
2024-01-17 20:46:59.558429: I tensorflow_serving/core/basic_manager.cc:739] Successfully reserved resources to load servable {name: s2d version: 1}
2024-01-17 20:46:59.558482: I tensorflow_serving/core/loader_harness.cc:66] Approving load for servable version {name: s2d version: 1}
2024-01-17 20:46:59.558494: I tensorflow_serving/core/loader_harness.cc:74] Loading servable version {name: s2d version: 1}
2024-01-17 20:46:59.558556: I external/org_tensorflow/tensorflow/cc/saved_model/reader.cc:83] Reading SavedModel from: /models/s2d/0000001
2024-01-17 20:46:59.610243: I external/org_tensorflow/tensorflow/cc/saved_model/reader.cc:51] Reading meta graph with tags { serve }
2024-01-17 20:46:59.610350: I external/org_tensorflow/tensorflow/cc/saved_model/reader.cc:146] Reading SavedModel debug info (if present) from: /models/s2d/0000001
2024-01-17 20:46:59.610463: I external/org_tensorflow/tensorflow/core/platform/cpu_feature_guard.cc:182] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
2024-01-17 20:46:59.714268: I external/org_tensorflow/tensorflow/compiler/mlir/mlir_graph_optimization_pass.cc:382] MLIR V1 optimization pass is not enabled
2024-01-17 20:46:59.741211: I external/org_tensorflow/tensorflow/cc/saved_model/loader.cc:233] Restoring SavedModel bundle.
2024-01-17 20:47:00.471974: I external/org_tensorflow/tensorflow/cc/saved_model/loader.cc:217] Running initialization op on SavedModel bundle at path: /models/s2d/0000001
2024-01-17 20:47:00.731464: I external/org_tensorflow/tensorflow/cc/saved_model/loader.cc:316] SavedModel load for tags { serve }; Status: success: OK. Took 1172904 microseconds.
2024-01-17 20:47:00.789732: I tensorflow_serving/servables/tensorflow/saved_model_warmup_util.cc:80] No warmup data file found at /models/s2d/0000001/assets.extra/tf_serving_warmup_requests
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