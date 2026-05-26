import type { ActionChip } from '@/types/agent'

interface Props {
  chips: ActionChip[]
  onAction: (chip: ActionChip) => void
}

export default function ActionChips({ chips, onAction }: Props) {
  if (chips.length === 0) return null

  return (
    <div className="flex flex-wrap gap-1 mt-2">
      {chips.map((chip, i) => (
        <button
          key={i}
          onClick={() => onAction(chip)}
          className="text-[10px] px-2 py-0.5 border border-agent/40 text-agent-text hover:bg-agent-surface rounded transition-colors"
        >
          {chip.label}
        </button>
      ))}
    </div>
  )
}
