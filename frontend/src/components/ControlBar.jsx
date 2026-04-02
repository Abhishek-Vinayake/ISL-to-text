export default function ControlBar({ isRunning, onStart, onStop }) {
  return (
    <div className="flex gap-4 px-6 pb-4">
      <button
        onClick={onStart}
        disabled={isRunning}
        className="px-4 py-2 rounded-lg border border-cyan-400 text-cyan-300
                   hover:bg-cyan-500/10 transition shadow-neon-cyan disabled:opacity-40"
      >
        Start
      </button>

      <button
        onClick={onStop}
        disabled={!isRunning}
        className="px-4 py-2 rounded-lg border border-pink-400 text-pink-300
                   hover:bg-pink-500/10 transition shadow-neon-pink disabled:opacity-40"
      >
        Stop
      </button>
    </div>
  );
}
