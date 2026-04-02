import numpy as np
import pickle
import cv2
import os
from collections import deque

# -------------------------------
# Load Model & Labels
# -------------------------------
import tensorflow as tf

BASE_DIR = os.path.dirname(__file__)

MODEL_PATH = os.path.join(BASE_DIR, "isl_gesture_model.h5")
LABEL_MAP_PATH = os.path.join(BASE_DIR, "label_map.pkl")

# Load trained model
model = tf.keras.models.load_model(MODEL_PATH)

# Load label mappings
with open(LABEL_MAP_PATH, "rb") as f:
    label_to_idx = pickle.load(f)

idx_to_label = {v: k for k, v in label_to_idx.items()}

# -------------------------------
# Constants (must match training)
# -------------------------------
SEQ_LEN = 32
FEATURE_SIZE = 138    # Change to 132 only if you removed palm duplication


# -------------------------------
# Mediapipe Holistic
# -------------------------------
import mediapipe as mp

mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    refine_face_landmarks=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


def extract_features(frame):
    """Extract 138-d / 132-d feature vector."""
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = holistic.process(image_rgb)

    vec = []

    # Pose shoulders (11, 12)
    if results.pose_landmarks:
        for idx in [11, 12]:
            lm = results.pose_landmarks.landmark[idx]
            vec.extend([lm.x, lm.y, lm.z])
    else:
        vec.extend([0.0] * 6)

    # 21 hand landmarks each (63 values)
    for hand in [results.left_hand_landmarks, results.right_hand_landmarks]:
        if hand:
            for lm in hand.landmark:
                vec.extend([lm.x, lm.y, lm.z])
        else:
            vec.extend([0.0] * 63)

    # IF FEATURE_SIZE = 138 → include palms
    if FEATURE_SIZE == 138:
        for hand in [results.left_hand_landmarks, results.right_hand_landmarks]:
            if hand:
                lm0 = hand.landmark[0]
                vec.extend([lm0.x, lm0.y, lm0.z])
            else:
                vec.extend([0.0] * 3)

    return np.array(vec, dtype=float)


# -------------------------------
# Inference
# -------------------------------
def run_inference(frame, seq_buffer: deque):
    """Process frame, update sequence, return prediction."""
    features = extract_features(frame)

    seq_buffer.append(features)

    # Not enough data yet
    if len(seq_buffer) < SEQ_LEN:
        return {"label": None, "confidence": 0.0}

    sequence = np.array(seq_buffer, dtype=float).reshape(1, SEQ_LEN, FEATURE_SIZE)

    # Prediction
    raw_probs = model.predict(sequence, verbose=0)[0]
    pred_idx = int(np.argmax(raw_probs))
    confidence = float(np.max(raw_probs))

    # Map index → label string
    pred_label = idx_to_label[pred_idx]

    return {
        "label": pred_label,
        "confidence": confidence,
    }
