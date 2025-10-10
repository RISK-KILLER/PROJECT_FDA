import React from 'react';
import useTypingEffect from '../hooks/useTypingEffect';
import TermTooltip from './TermTooltip';
import CitationLink from './CitationLink';

const TypingMessage = ({ message, speed = 15, citations }) => {
  const { displayText, isComplete } = useTypingEffect(message.content, speed);
  
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
  
  return (
    <div className="whitespace-pre-wrap">
      {(() => {
        const citationRegex = /\[(\d+)\]/g;
        const parts = [];
        let lastIndex = 0;
        let match;
        let key = 0;

        while ((match = citationRegex.exec(displayText)) !== null) {
          if (match.index > lastIndex) {
            parts.push(
              <span key={`text-${key++}`}>
                {displayText.substring(lastIndex, match.index)}
              </span>
            );
          }

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

        if (lastIndex < displayText.length) {
          parts.push(
            <span key={`text-${key++}`}>
              {displayText.substring(lastIndex)}
            </span>
          );
        }

        return parts;
      })()}
      {!isComplete && <span className="animate-pulse">|</span>}
    </div>
  );
};

export default TypingMessage;
