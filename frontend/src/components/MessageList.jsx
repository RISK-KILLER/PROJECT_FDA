import React, { memo } from 'react';
import { MessageCircle, FileText, Download } from 'lucide-react';
import PromptChips from './PromptChips';
import ScenarioCards from './ScenarioCards';
import SampleSnippets from './SampleSnippets';

const MessageList = ({ messages, isTyping, onGenerateChecklist, onDownloadReport, setInputMessage, sendMessage }) => {
  return (
    <div className="flex-1 p-6 overflow-y-auto space-y-6">
      {messages.map(message => (
        <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
          <div className={`max-w-[70%] rounded-2xl px-6 py-4 ${
            message.type === 'user'
              ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-br-md'
              : 'bg-gray-50 border border-gray-200 rounded-bl-md'
          }`}>
            <div className="whitespace-pre-wrap">{message.content}</div>

            <PromptChips 
              chips={message.chips} 
              setInputMessage={setInputMessage} 
              sendMessage={sendMessage} 
            />

            <ScenarioCards 
              scenarios={message.scenarios} 
              setInputMessage={setInputMessage} 
              sendMessage={sendMessage} 
            />

            <SampleSnippets samples={message.samples} />

            {message.type === 'bot' && !message.chips && (
              <div className="flex gap-2 mt-4">
                <button 
                  onClick={onGenerateChecklist}
                  className="flex items-center gap-1 bg-indigo-100 text-indigo-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-indigo-200 transition-colors"
                >
                  <FileText className="w-4 h-4" />
                  체크리스트 생성
                </button>
                <button 
                  onClick={onDownloadReport}
                  className="flex items-center gap-1 bg-indigo-100 text-indigo-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-indigo-200 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  보고서 다운로드
                </button>
              </div>
            )}
          </div>
        </div>
      ))}

      {isTyping && (
        <div className="flex justify-start">
          <div className="bg-gray-50 border border-gray-200 rounded-2xl rounded-bl-md px-6 py-4 max-w-[70%]">
            <div className="flex items-center gap-1">
              <MessageCircle className="w-4 h-4 text-gray-500" />
              <span className="text-gray-500 italic">AI가 응답을 생성중입니다...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default memo(MessageList);


