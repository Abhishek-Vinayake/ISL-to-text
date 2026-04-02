import { useState, useCallback } from "react";
import Header from "./components/Header";
import ControlBar from "./components/ControlBar";
import WebcamPanel from "./components/WebcamPanel";
import { usePredictionSocket } from "./hooks/usePredictionSocket";

export default function App() {
  const [isRunning, setIsRunning] = useState(false);
  const [prediction, setPrediction] = useState(null);

  const handlePrediction = useCallback((data) => {
    setPrediction({
      label: data.label,
      confidence: data.confidence,
      landmarks: data.landmarks || [],
    });
  }, []);

  const { sendFrame } = usePredictionSocket({
    isRunning,
    onPrediction: handlePrediction,
  });

  return (
    <div className="min-h-screen cyber-gradient text-white">
      <Header />

      <ControlBar
        isRunning={isRunning}
        onStart={() => setIsRunning(true)}
        onStop={() => setIsRunning(false)}
      />

      <main className="px-6 pb-8 flex flex-col items-center">
        <WebcamPanel
          isRunning={isRunning}
          sendFrame={sendFrame}
          prediction={prediction}
        />
      </main>
    </div>
  );
}
