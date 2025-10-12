import React, { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { MessageCircle, FileText, Download, Clock } from 'lucide-react';
import PromptChips from './PromptChips';
import ScenarioCards from './ScenarioCards';
import SampleSnippets from './SampleSnippets';
import TypingMessage from './TypingMessage';
import TermTooltip from './TermTooltip';
import CitationLink from './CitationLink';
import CitationsList from './CitationsList';

const MessageList = ({ messages, isTyping, elapsedTime, onGenerateChecklist, onDownloadReport, setInputMessage, sendMessage }) => {
  
  const formatTime = (ms) => {
    if (!ms) return '';
    return (ms / 1000).toFixed(1);
  };

  // FDA 용어를 감지하고 툴팁으로 감싸는 함수
  const renderTextWithTerms = (text) => {
    if (!text) return text;
    
    // FDA 용어 목록 (정규식으로 정확한 매칭)
    const fdaTerms = ['FSVP', 'GRAS', 'RPM', 'GWPE', 'HACCP', 'CGMP', 'FDA', 'CFR'];
    const termRegex = new RegExp(`\\b(${fdaTerms.join('|')})\\b`, 'gi');
    
    const parts = text.split(termRegex);
    const matches = text.match(termRegex) || [];
    
    return parts.map((part, index) => {
      if (index < matches.length) {
        const term = matches[index].toUpperCase();
        return (
          <React.Fragment key={index}>
            {part}
            <TermTooltip term={term} />
          </React.Fragment>
        );
      }
      return part;
    });
  };

  // 마크다운 문법을 파싱하는 함수
  const parseMarkdown = (text) => {
    if (!text) return text;
    
    // 굵은 글씨 처리: **텍스트** -> <strong>텍스트</strong>
    let processedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // 기울임 처리: *텍스트* -> <em>텍스트</em>
    processedText = processedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return processedText;
  };

  // 메시지 내용에서 [1], [2] 같은 citation을 찾아서 링크로 변환
  const renderContentWithCitations = (content, citations) => {
    if (!content) return content;
    
    const citationRegex = /\[(\d+)\]/g;
    const parts = [];
    let lastIndex = 0;
    let match;
    let key = 0;

    while ((match = citationRegex.exec(content)) !== null) {
      // Citation 이전 텍스트
      if (match.index > lastIndex) {
        const textPart = content.substring(lastIndex, match.index);
        // 마크다운 파싱 후 FDA 용어 처리
        const markdownParsed = parseMarkdown(textPart);
        parts.push(
          <span key={`text-${key++}`} dangerouslySetInnerHTML={{ __html: markdownParsed }} />
        );
      }

      // Citation 링크
      const citationNum = parseInt(match[1]);
      const citation = citations?.find(c => c.index === citationNum);
      
      parts.push(
        <CitationLink
          key={`cite-${key++}`}
          number={citationNum}
          url={citation?.url}
          title={citation?.title}
        />
      );

      lastIndex = match.index + match[0].length;
    }

    // 남은 텍스트
    if (lastIndex < content.length) {
      const textPart = content.substring(lastIndex);
      // 마크다운 파싱 후 FDA 용어 처리
      const markdownParsed = parseMarkdown(textPart);
      parts.push(
        <span key={`text-${key++}`} dangerouslySetInnerHTML={{ __html: markdownParsed }} />
      );
    }

    return parts;
  };

  return (
    <div className="flex-1 p-2 lg:p-4 overflow-y-auto space-y-6">
      {messages.map(message => (
        <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
          <div className={`${message.type === 'user' ? 'max-w-[85%]' : 'w-full'} rounded-2xl px-6 py-4 ${
            message.type === 'user'
              ? 'bg-gradient-to-r from-indigo-500 to-indigo-600 text-white rounded-br-md'
              : 'bg-purple-50/40 border border-purple-100 rounded-bl-md'
          }`}>
            {message.type === 'bot' ? (
              <>
                <TypingMessage message={message} speed={8} citations={message.citations} />
                
                {/* Citations 목록 추가 */}
                {message.citations && message.citations.length > 0 && (
                  <CitationsList citations={message.citations} />
                )}
              </>
            ) : (
              <div className="whitespace-pre-wrap">
                {renderContentWithCitations(message.content, message.citations)}
              </div>
            )}

            {/* 응답 시간 표시 */}
            {message.type === 'bot' && (message.responseTime || message.agentResponseTime) && (
              <div className="flex items-center gap-2 mt-3 text-xs text-gray-500 border-t border-purple-100 pt-2 response-time">
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

          </div>
        </div>
      ))}

      {/* 실시간 타이머 로딩 */}
      {isTyping && (
        <div className="flex justify-start">
          <div className="bg-purple-50/40 border border-purple-100 rounded-2xl rounded-bl-md px-6 py-4 w-fit">
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