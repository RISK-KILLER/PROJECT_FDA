import React from 'react';

const ScenarioCards = ({ scenarios, setInputMessage, sendMessage }) => {
  if (!scenarios || scenarios.length === 0) return null;

  return (
    <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
      {scenarios.map((sc, i) => (
        <div key={i} className="p-3 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 transition-colors">
          <div className="text-sm font-semibold text-gray-800">{sc.title}</div>
          <div className="text-xs text-gray-500 mt-1">{sc.summary}</div>
          <div className="mt-2 flex gap-2">
            <button
              onClick={() => setInputMessage(sc.prompt)}
              className="text-xs px-2 py-1 rounded border border-indigo-200 text-indigo-700 hover:bg-indigo-50"
            >
              예시 질문 넣기
            </button>
            <button
              onClick={() => { setInputMessage(sc.prompt); setTimeout(() => { sendMessage(); }, 0); }}
              className="text-xs px-2 py-1 rounded bg-indigo-600 text-white hover:bg-indigo-700"
            >
              바로 질문
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ScenarioCards;
