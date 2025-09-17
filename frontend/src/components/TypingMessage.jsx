import React from 'react';
import useTypingEffect from '../hooks/useTypingEffect';

const TypingMessage = ({ message, speed = 15 }) => {
  const { displayText, isComplete } = useTypingEffect(message.content, speed);
  
  return (
    <div className="whitespace-pre-wrap">
      {displayText}
      {!isComplete && <span className="animate-pulse">|</span>}
    </div>
  );
};

export default TypingMessage;
