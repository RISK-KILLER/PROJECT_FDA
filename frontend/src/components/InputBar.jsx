import React from 'react';

const InputBar = ({ inputMessage, setInputMessage, isTyping, onSend, onKeyPress, onDrop, onDragOver, onDragLeave, dragOver, fileInputRef, onFileChange, isCentered = false }) => {
  const containerClass = isCentered 
    ? "w-full" 
    : "p-3 lg:p-6 border-t border-purple-100 bg-purple-50/30";
    
  const inputClass = isCentered
    ? "w-full border border-gray-300 rounded-xl px-3 lg:px-4 py-3 lg:py-4 resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-base lg:text-lg"
    : "w-full border border-gray-300 rounded-xl px-3 lg:px-4 py-2 lg:py-3 resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-sm lg:text-base";

  return (
    <div className={containerClass}>
      <div className="flex gap-2 lg:gap-3 items-end">
        {/* 파일 업로드 버튼 */}
        <button
          onClick={() => fileInputRef.current?.click()}
          className="flex-shrink-0 w-8 h-8 lg:w-10 lg:h-10 flex items-center justify-center border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-colors text-sm lg:text-base"
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
          className="bg-gradient-to-r from-indigo-500 to-indigo-600 text-white px-3 lg:px-6 py-2 lg:py-3 rounded-xl hover:from-indigo-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 text-sm lg:text-base whitespace-nowrap"
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


