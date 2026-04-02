import os
import pickle
import numpy as np
import tensorflow as tf
from typing import Tuple


# ------------------------------
# Paths
# ------------------------------
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "model")
MODEL_PATH = os.path.join(MODEL_DIR, "isl_gesture_model.tflite")
LABEL_MAP_PATH = os.path.join(MODEL_DIR, "label_map.pkl")


# ------------------------------
# Gesture Model Loader
# ------------------------------
class GestureModel:
    def __init__(self):
        print("Loading TFLite model:", MODEL_PATH)

        # Load interpreter
        self.interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
        self.interpreter.allocate_tensors()

        # Store details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        print("\nTFLite input details:")
        for d in self.input_details:
            print(" ", d)

        print("\nTFLite output details:")
        for d in self.output_details:
            print(" ", d)

        # Load label map
        with open(LABEL_MAP_PATH, "rb") as f:
            self.label_map = pickle.load(f)

        print("\nLoaded label map:", self.label_map)
        print("-" * 50)

    # ------------------------------------------
    # PREDICT
    # ------------------------------------------
    def predict(self, features: np.ndarray) -> Tuple[str, float]:
        """
        Takes a feature tensor (should be 1×32×138),
        reshapes if needed, feeds to TFLite, returns (label, confidence).
        """

        input_shape = self.input_details[0]["shape"]
        input_dtype = self.input_details[0]["dtype"]

        try:
            input_data = np.array(features, dtype=input_dtype)

            # Expected number of elements
            expected_size = int(np.prod(input_shape))
            current_size = input_data.size

            if current_size != expected_size:
                raise ValueError(
                    f"[ERROR] Feature size mismatch! "
                    f"Model expects {expected_size}, got {current_size}. "
                    f"Expected shape {input_shape}, got {features.shape}"
                )

            # Reshape to required model input
            input_data = input_data.reshape(tuple(input_shape)).astype(input_dtype)

        except Exception as e:
            raise RuntimeError(f"Failed to prepare input tensor: {e}")

        # ---- RUN MODEL ----
        self.interpreter.set_tensor(self.input_details[0]["index"], input_data)
        self.interpreter.invoke()

        output_data = self.interpreter.get_tensor(self.output_details[0]["index"])
        probs = output_data[0]

        # Pick label
        class_idx = int(np.argmax(probs))
        confidence = float(probs[class_idx])

        if isinstance(self.label_map, dict):
            label = self.label_map.get(class_idx, str(class_idx))
        else:
            label = self.label_map[class_idx]

        # --------------------------------------
        # RAW DEBUG PRINT (IMPORTANT)
        # --------------------------------------
        print("RAW PROBS:", probs, "   PRED:", label, "   CONF:", confidence)

        return label, confidence


# ------------------------------
# GLOBAL MODEL INSTANCE
# ------------------------------
gesture_model = GestureModel()
