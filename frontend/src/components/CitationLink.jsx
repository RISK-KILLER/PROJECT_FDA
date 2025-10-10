import React from 'react';

/**
 * [1], [2] 클릭 시 해당 URL로 직접 이동
 */
const CitationLink = ({ number, url, title }) => {
  // URL이 없거나 빈 문자열이면 일반 텍스트로 표시
  if (!url || url.trim() === '') {
    return (
      <span className="inline-block text-blue-600 font-semibold text-sm align-super mx-0.5">
        [{number}]
      </span>
    );
  }

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-block text-blue-600 hover:text-blue-800 
                 font-semibold text-sm align-super mx-0.5 
                 transition-colors duration-150 no-underline hover:underline
                 cursor-pointer"
      title={`참고자료 ${number}번: ${title || '링크로 이동'}`}
    >
      [{number}]
    </a>
  );
};

export default CitationLink;
