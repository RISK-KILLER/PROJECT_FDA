import React, { useState } from 'react';
import { FileText, ExternalLink, ChevronDown, ChevronRight } from 'lucide-react';

/**
 * 메시지 하단의 참고자료 목록 (토글 가능, 클릭 시 URL 이동)
 */
const CitationsList = ({ citations }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!citations || citations.length === 0) {
    return null;
  }

  const getCollectionBadgeColor = (collection) => {
    const colors = {
      guidance: 'bg-blue-100 text-blue-700',
      ecfr: 'bg-purple-100 text-purple-700',
      dwpe: 'bg-red-100 text-red-700',
      gras: 'bg-green-100 text-green-700',
      fsvp: 'bg-yellow-100 text-yellow-700',
      usc: 'bg-gray-100 text-gray-700'
    };
    return colors[collection] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="mt-6 pt-4 border-t-2 border-purple-200">
      {/* 토글 헤더 */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-2 rounded-lg 
                   hover:bg-gray-50 transition-colors duration-200
                   focus:outline-none focus:ring-2 focus:ring-purple-300"
        aria-expanded={isExpanded}
        aria-label={`참고자료 ${isExpanded ? '접기' : '펼치기'}`}
      >
        <h4 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
          <FileText className="w-4 h-4" />
          참고자료 ({citations.length}개)
        </h4>
        
        {/* 토글 아이콘 */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">
            {isExpanded ? '접기' : '펼치기'}
          </span>
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-gray-500 transition-transform duration-200" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-500 transition-transform duration-200" />
          )}
        </div>
      </button>
      
      {/* 접기/펼치기 애니메이션 */}
      <div 
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isExpanded ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="space-y-2 mt-3">
          {citations.map((citation) => (
            <div
              key={citation.index}
              className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg 
                         hover:bg-gray-100 transition-all duration-200"
            >
              {/* Citation 번호 */}
              <span className="text-blue-600 font-semibold text-sm min-w-[30px] mt-0.5">
                [{citation.index}]
              </span>

              {/* Collection 뱃지 */}
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium 
                            ${getCollectionBadgeColor(citation.collection)} 
                            flex items-center gap-1 flex-shrink-0`}
              >
                {citation.collection}
              </span>

              {/* 제목 및 링크 */}
              <div className="flex-1 min-w-0">
                {citation.url ? (
                  <a
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-700 hover:text-blue-600 text-sm 
                               flex items-center gap-1 group break-words"
                  >
                    <span className="break-words">{citation.title}</span>
                    <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 
                                            transition-opacity flex-shrink-0" />
                  </a>
                ) : (
                  <span className="text-gray-700 text-sm break-words">
                    {citation.title}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CitationsList;
