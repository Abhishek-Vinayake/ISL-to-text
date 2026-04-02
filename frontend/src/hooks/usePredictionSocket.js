import { useEffect, useRef } from "react";

export function usePredictionSocket({ isRunning, onPrediction }) {
  const socketRef = useRef(null);

  useEffect(() => {
    if (isRunning) {
      const ws = new WebSocket("ws://127.0.0.1:8000/ws/predict");
      socketRef.current = ws;

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "prediction") {
          onPrediction(data);
        }
      };

      return () => ws.close();
    } else {
      if (socketRef.current) {
        socketRef.current.close();
      }
    }
  }, [isRunning]);

  const sendFrame = (dataUrl) => {
    if (!isRunning) return;
    if (!socketRef.current) return;
    if (socketRef.current.readyState !== WebSocket.OPEN) return;

    socketRef.current.send(
      JSON.stringify({
        type: "frame",
        image: dataUrl,
      })
    );
  };

  return { sendFrame };
}
