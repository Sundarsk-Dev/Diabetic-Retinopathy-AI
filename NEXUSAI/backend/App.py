from flask import Flask, request, jsonify, render_template, Response
import tensorflow as tf
import numpy as np
import cv2
from flask_cors import CORS  # ✅ Allow frontend requests from other ports

app = Flask(__name__)
CORS(app)  # ✅ Enable Cross-Origin Resource Sharing

# ✅ Load the trained model ONCE at start, with error handling
try:
    model = tf.keras.models.load_model("diabetic_retinopathy_vit.h5")
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None  # Prevents crashes if model fails to load

# Class Labels
class_labels = ['Healthy', 'Mild DR', 'Moderate DR', 'Proliferative DR', 'Severe DR']

# **🔹 Preprocess Image for Model**
def preprocess_image(image):
    try:
        img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
        img = cv2.resize(img, (299, 299))  # Resize for InceptionV3
        img = img / 255.0  # Normalize
        img = np.expand_dims(img, axis=0)  # Add batch dimension
        return img
    except Exception as e:
        print(f"❌ Error preprocessing image: {e}")
        return None

# **🔹 API for Image Upload & Prediction**
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    image = preprocess_image(file)
    if image is None:
        return jsonify({"error": "Invalid image format"}), 400

    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    # Predict using loaded model
    try:
        prediction = model.predict(image)
        class_index = np.argmax(prediction)
        confidence = np.max(prediction)
        result_text = f"{class_labels[class_index]} ({confidence*100:.2f}%)"
        return jsonify({"result": result_text})
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return jsonify({"error": "Prediction failed"}), 500

# **🔹 Live Webcam Prediction**
def generate_frames():
    cap = cv2.VideoCapture(0)  # Open webcam
    if not cap.isOpened():
        print("❌ Error: Could not access webcam")
        return

    while True:
        success, frame = cap.read()
        if not success:
            print("❌ Error: Failed to capture frame")
            break

        # Preprocess frame for model
        try:
            img = cv2.resize(frame, (299, 299))
            img = img / 255.0  # Normalize
            img = np.expand_dims(img, axis=0)

            # Predict
            prediction = model.predict(img)
            class_index = np.argmax(prediction)
            confidence = np.max(prediction)
            text = f"{class_labels[class_index]} ({confidence*100:.2f}%)"

            # Display prediction on the frame
            cv2.putText(frame, text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Convert frame to JPEG format
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # Yield frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        except Exception as e:
            print(f"❌ Webcam prediction error: {e}")
            break

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# **🔹 Serve Frontend**
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # ✅ Explicitly setting port 5000
