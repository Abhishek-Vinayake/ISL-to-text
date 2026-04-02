import cv2
import numpy as np
import mediapipe as mp
from typing import List, Optional, Tuple


mp_hands = mp.solutions.hands


class MediaPipeHandDetector:
    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_hands: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        self.hands = mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process(
        self, image_bgr: np.ndarray
    ) -> Tuple[Optional[List[Tuple[float, float, float]]], np.ndarray]:
        """
        image_bgr: BGR image from OpenCV
        returns: (landmarks_list or None, image_rgb)
        landmarks_list: list of (x, y, z) normalized coordinates for first hand
        """
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append((lm.x, lm.y, lm.z))
            return landmarks, image_rgb

        return None, image_rgb


# Singleton detector
hand_detector = MediaPipeHandDetector()
