import { useState, useEffect } from 'react';

const useTypingEffect = (text, speed = 50) => {
  const [displayText, setDisplayText] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  
  useEffect(() => {
    if (!text) {
      setDisplayText('');
      setIsComplete(false);
      return;
    }
    
    let i = 0;
    setDisplayText('');
    setIsComplete(false);
    
    const timer = setInterval(() => {
      setDisplayText(text.slice(0, i));
      i++;
      
      if (i > text.length) {
        clearInterval(timer);
        setIsComplete(true);
      }
    }, speed);
    
    return () => clearInterval(timer);
  }, [text, speed]);
  
  return { displayText, isComplete };
};

export default useTypingEffect;
