import { useEffect, useRef } from "react";

export default function WebcamPanel({ isRunning, sendFrame, prediction }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    async function startCamera() {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
      });

      videoRef.current.srcObject = stream;
      await videoRef.current.play();

      startSendingFrames();
    }

    function stopCamera() {
      if (intervalRef.current) clearInterval(intervalRef.current);

      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach((t) => t.stop());
        videoRef.current.srcObject = null;
      }
    }

    function startSendingFrames() {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");

      intervalRef.current = setInterval(() => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        ctx.drawImage(video, 0, 0);
        sendFrame(canvas.toDataURL("image/jpeg", 0.7));
      }, 100);
    }

    if (isRunning) startCamera();
    else stopCamera();

    return () => stopCamera();
  }, [isRunning]);


  return (
    <div className="
        relative w-full max-w-6xl mx-auto 
        rounded-3xl border border-cyan-500/40 
        bg-cyber-panel shadow-neon-cyan overflow-hidden
      "
    >
      {/* Video container */}
      <div className="relative w-full aspect-video bg-black rounded-3xl overflow-hidden">

        {!isRunning && (
          <div className="absolute inset-0 flex items-center justify-center text-slate-500">
            Press Start to activate webcam
          </div>
        )}

        <video
          ref={videoRef}
          className={`w-full h-full object-cover ${isRunning ? "" : "hidden"} transform -scale-x-100`}
        />

        <canvas ref={canvasRef} className="hidden" />

        {/* Slightly larger prediction overlay (Option A) */}
        <div
          className="
            absolute bottom-5 left-1/2 -translate-x-1/2 
            px-8 py-4 rounded-2xl
            bg-black/60 backdrop-blur-sm
            border border-cyan-400/60 
            shadow-neon-cyan
          "
        >
          <div className="text-xs uppercase tracking-wide text-slate-400 mb-1">
            Prediction
          </div>

          <div className="flex items-baseline gap-3">
            <div className="text-2xl font-semibold text-cyan-300">
              {prediction?.label || "No gesture"}
            </div>

            <div className="text-sm text-slate-400">
              {prediction?.confidence
                ? (prediction.confidence * 100).toFixed(1) + "%"
                : ""}
            </div>
          </div>

          {/* Confidence bar */}
          <div className="mt-3 h-2 w-64 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="
                h-full bg-gradient-to-r 
                from-cyan-400 via-fuchsia-400 to-pink-500
                transition-all duration-150
              "
              style={{
                width: `${
                  prediction?.confidence
                    ? Math.min(prediction.confidence * 100, 100)
                    : 0
                }%`,
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
