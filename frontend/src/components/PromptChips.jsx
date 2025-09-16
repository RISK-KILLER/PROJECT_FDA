import React from 'react';

const PromptChips = ({ chips, setInputMessage, sendMessage }) => {
  if (!chips || chips.length === 0) return null;

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {chips.map((chip, idx) => (
        <div key={idx} className="flex items-center">
          <button
            onClick={() => setInputMessage(chip.prompt || chip.label)}
            className="px-3 py-1 text-xs rounded-full bg-indigo-100 text-indigo-700 border border-indigo-200 hover:bg-indigo-200 transition-colors"
            aria-label={`${chip.label} 주제로 질문하기`}
          >
            {chip.label}
          </button>
          <button
            onClick={() => {
              const text = chip.prompt || chip.label;
              setInputMessage(text);
              setTimeout(() => { sendMessage(); }, 0);
            }}
            className="ml-1 px-2 py-1 text-[10px] rounded-full bg-white text-indigo-600 border border-indigo-200 hover:bg-indigo-50"
            aria-label={`${chip.label} 바로 질문`}
          >
            바로 질문
          </button>
        </div>
      ))}
    </div>
  );
};

export default PromptChips;
