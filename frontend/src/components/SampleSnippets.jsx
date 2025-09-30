import React from 'react';

const SampleSnippets = ({ samples }) => {
  if (!samples || samples.length === 0) return null;

  return (
    <div className="mt-4 space-y-2">
      {samples.map((s, idx) => (
        <div key={idx} className="text-xs text-gray-700 bg-gray-50 border border-gray-200 rounded p-3">
          <div><span className="font-semibold text-indigo-600">USER:</span> {s.user}</div>
          <div className="mt-1"><span className="font-semibold text-indigo-700">BOT:</span> {s.bot}</div>
        </div>
      ))}
    </div>
  );
};

export default SampleSnippets;
