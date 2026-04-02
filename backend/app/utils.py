import time
from collections import deque
from typing import Deque, Tuple, Optional


class FPSCounter:
    def __init__(self, maxlen: int = 30):
        self.times: Deque[float] = deque(maxlen=maxlen)

    def tick(self) -> float:
        now = time.time()
        self.times.append(now)
        if len(self.times) < 2:
            return 0.0
        duration = self.times[-1] - self.times[0]
        if duration == 0:
            return 0.0
        return len(self.times) / duration


class PredictionSmoother:
    """
    Simple temporal smoothing:
    - Keeps last N (label, confidence)
    - Returns the majority label (if enough confidence)
    """

    def __init__(self, window_size: int = 5, min_confidence: float = 0.5):
        self.window_size = window_size
        self.min_confidence = min_confidence
        self.buffer: Deque[Tuple[Optional[str], float]] = deque(maxlen=window_size)

    def add(self, label: Optional[str], confidence: float):
        self.buffer.append((label, confidence))

    def get_smoothed(self) -> Tuple[Optional[str], float]:
        if not self.buffer:
            return None, 0.0

        # Count votes for labels above threshold
        counts = {}
        for label, conf in self.buffer:
            if label is None:
                continue
            if conf < self.min_confidence:
                continue
            counts[label] = counts.get(label, 0) + conf  # weighted by confidence

        if not counts:
            # Fallback to last prediction
            return self.buffer[-1]

        best_label = max(counts, key=counts.get)
        best_conf = counts[best_label] / self.window_size
        return best_label, best_conf
