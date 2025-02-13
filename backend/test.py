import tensorflow as tf

model_path = "C:\\Users\\User\\ML Predictor\\backend\\app\\trained_model\\random_model"

try:
    model = tf.keras.models.load_model(model_path)
    print("Model loaded successfully!")
except Exception as e:
    print("Error loading model:", e)
