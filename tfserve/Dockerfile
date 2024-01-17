# Use the official TensorFlow Serving image as the base image
FROM tensorflow/serving

# Set the working directory inside the container
WORKDIR /models

# Copy the saved model to the container
COPY ./model /models/s2d

# Expose the port on which TensorFlow Serving will listen
EXPOSE 8501

# Set environment variables
ENV MODEL_NAME s2d

# Start TensorFlow Serving when the container starts
CMD ["tensorflow_model_server", "--port=8500", "--rest_api_port=8501", "--model_name=s2d", "--model_base_path=/models/s2d"]
