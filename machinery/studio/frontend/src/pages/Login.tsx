import { useNavigate } from 'react-router-dom'

export default function Login() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center">
      <div className="w-[480px] border border-border rounded-lg bg-panel p-8 flex flex-col gap-6">
        <div className="text-center">
          <div className="text-3xl mb-2">⬡</div>
          <h1 className="text-xl font-mono text-text-primary">Texgraph Studio</h1>
          <p className="text-text-muted text-sm italic mt-1">
            Markdown → LuaLaTeX → PDF/X
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <button
            onClick={() => navigate('/projects')}
            className="w-full py-2 px-4 bg-accent hover:bg-accent-hover text-white rounded text-sm font-mono transition-colors"
          >
            Open Local Workspace
          </button>
          <button
            onClick={() => navigate('/projects')}
            className="w-full py-2 px-4 border border-border text-text-secondary hover:text-text-primary hover:border-accent rounded text-sm font-mono transition-colors"
          >
            Sign In
          </button>
        </div>

        <p className="text-center text-text-muted text-xs">
          v0.1.0 · MIT License
        </p>
      </div>
    </div>
  )
}
