import React from 'react';
import { Upload, Send } from 'lucide-react';

const InputBar = ({ inputMessage, setInputMessage, isTyping, onSend, onKeyPress, onDrop, onDragOver, onDragLeave, dragOver, fileInputRef, onFileChange }) => {
  return (
    <div className="p-6 border-t border-gray-200 bg-white/80">
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center mb-4 transition-colors cursor-pointer ${
          dragOver 
            ? 'border-indigo-500 bg-indigo-50' 
            : 'border-gray-300 hover:border-indigo-400 hover:bg-indigo-50'
        }`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-500">인증서, 분석서, 제품 문서를 업로드하세요</p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,.pdf"
          className="hidden"
          onChange={onFileChange}
        />
      </div>

      <div className="flex gap-4 items-end">
        <div className="flex-1">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={onKeyPress}
            placeholder="추가 질문이나 업로드한 문서에 대해 문의하세요..."
            className="w-full border border-gray-300 rounded-xl px-4 py-3 resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            rows={2}
          />
        </div>
        <button
          onClick={onSend}
          disabled={!inputMessage.trim() || isTyping}
          className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
        >
          <Send className="w-4 h-4" />
          전송
        </button>
      </div>
    </div>
  );
};

export default InputBar;


