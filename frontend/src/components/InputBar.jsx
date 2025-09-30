import React from 'react';

const InputBar = ({ inputMessage, setInputMessage, isTyping, onSend, onKeyPress, onDrop, onDragOver, onDragLeave, dragOver, fileInputRef, onFileChange, isCentered = false }) => {
  const containerClass = isCentered 
    ? "w-full" 
    : "p-6 border-t border-gray-200 bg-white/80";
    
  const inputClass = isCentered
    ? "w-full border border-gray-300 rounded-xl px-4 py-4 resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-lg"
    : "w-full border border-gray-300 rounded-xl px-4 py-3 resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all";

  return (
    <div className={containerClass}>
      <div className="flex gap-3 items-end">
        {/* 파일 업로드 버튼 */}
        <button
          onClick={() => fileInputRef.current?.click()}
          className="flex-shrink-0 w-10 h-10 flex items-center justify-center border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-colors"
          title="파일 업로드"
        >
          +
        </button>
        
        {/* 텍스트 입력 영역 */}
        <div className="flex-1">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={onKeyPress}
            placeholder={isCentered ? "오늘 어떤 도움을 드릴까요?" : "추가 질문이나 업로드한 문서에 대해 문의하세요..."}
            className={inputClass}
            rows={isCentered ? 1 : 2}
          />
        </div>
        
        {/* 전송 버튼 */}
        <button
          onClick={onSend}
          disabled={!inputMessage.trim() || isTyping}
          className="bg-gradient-to-r from-indigo-500 to-indigo-600 text-white px-6 py-3 rounded-xl hover:from-indigo-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          {isCentered ? "→" : "전송"}
        </button>
      </div>
      
      {/* 숨겨진 파일 입력 */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*,.pdf"
        className="hidden"
        onChange={onFileChange}
      />
    </div>
  );
};

export default InputBar;


