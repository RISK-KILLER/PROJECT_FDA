import React, { memo } from 'react';
import { MessageCircle, FileText, Download, Clock } from 'lucide-react';
import PromptChips from './PromptChips';
import ScenarioCards from './ScenarioCards';
import SampleSnippets from './SampleSnippets';
import TypingMessage from './TypingMessage';

const MessageList = ({ messages, isTyping, elapsedTime, onGenerateChecklist, onDownloadReport, setInputMessage, sendMessage }) => {
  
  const formatTime = (ms) => {
    if (!ms) return '';
    return (ms / 1000).toFixed(1);
  };

  return (
    <div className="flex-1 p-6 overflow-y-auto space-y-6">
      {messages.map(message => (
        <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
          <div className={`max-w-[70%] rounded-2xl px-6 py-4 ${
            message.type === 'user'
              ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-br-md'
              : 'bg-gray-50 border border-gray-200 rounded-bl-md'
          }`}>
            {message.type === 'bot' ? (
              <TypingMessage message={message} speed={15} />
            ) : (
              <div className="whitespace-pre-wrap">{message.content}</div>
            )}

            {/* 응답 시간 표시 */}
            {message.type === 'bot' && (message.responseTime || message.agentResponseTime) && (
              <div className="flex items-center gap-2 mt-3 text-xs text-gray-500 border-t border-gray-200 pt-2 response-time">
                <Clock className="w-3 h-3" />
                {message.responseTime && (
                  <span>전체: {formatTime(message.responseTime)}s</span>
                )}
                {message.agentResponseTime && (
                  <>
                    {message.responseTime && <span>|</span>}
                    <span>에이전트: {formatTime(message.agentResponseTime)}s</span>
                  </>
                )}
                {message.timestamp && (
                  <span className="ml-auto opacity-70">
                    {new Date().toLocaleTimeString('ko-KR', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                )}
              </div>
            )}

            <PromptChips chips={message.chips} setInputMessage={setInputMessage} sendMessage={sendMessage} />
            <ScenarioCards scenarios={message.scenarios} setInputMessage={setInputMessage} sendMessage={sendMessage} />
            <SampleSnippets samples={message.samples} />

            {message.type === 'bot' && !message.chips && (
              <div className="flex gap-2 mt-4">
                <button onClick={onGenerateChecklist} className="flex items-center gap-1 bg-indigo-100 text-indigo-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-indigo-200 transition-colors">
                  <FileText className="w-4 h-4" />
                  체크리스트 생성
                </button>
                <button onClick={onDownloadReport} className="flex items-center gap-1 bg-indigo-100 text-indigo-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-indigo-200 transition-colors">
                  <Download className="w-4 h-4" />
                  보고서 다운로드
                </button>
              </div>
            )}
          </div>
        </div>
      ))}

      {/* 실시간 타이머 로딩 */}
      {isTyping && (
        <div className="flex justify-start">
          <div className="bg-gray-50 border border-gray-200 rounded-2xl rounded-bl-md px-6 py-4 max-w-[70%]">
            <div className="flex items-center gap-2 mb-3">
              <MessageCircle className="w-4 h-4 text-gray-500" />
              <span className="text-gray-500 italic">AI가 응답을 생성중입니다...</span>
            </div>
            
            <div className="flex items-center gap-3 mb-3">
              <div className="typing-dots">
                <span></span><span></span><span></span>
              </div>
              <span className="text-xs text-gray-400">문서를 찾고 있어요</span>
            </div>
            
            <div className="flex items-center gap-1 text-xs text-indigo-600 bg-indigo-50 px-3 py-2 rounded-lg timer-pulse">
              <Clock className="w-3 h-3" />
              <span className="font-mono font-semibold">{formatTime(elapsedTime || 0)}s</span>
              <span>경과</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default memo(MessageList);