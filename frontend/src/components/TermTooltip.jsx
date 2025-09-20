import React, { useState } from 'react';
import { Info, X, ExternalLink } from 'lucide-react';

const TermTooltip = ({ term, children, className = "" }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const [showPopup, setShowPopup] = useState(false);

  // FDA 용어 데이터베이스
  const termDatabase = {
    'FSVP': {
      fullName: 'Foreign Supplier Verification Programs',
      koreanName: '해외 공급자 검증 프로그램',
      description: '미국 식품 수입자가 해외 공급자로부터 식품을 수입할 때, 해당 공급자가 FDA 규정을 준수하는지 검증해야 하는 프로그램입니다.',
      details: [
        '수입자는 해외 공급자의 식품 안전 시스템을 평가해야 함',
        '공급자 검증 활동을 문서화하고 기록 보관',
        '위험 기반 접근법으로 검증 빈도 결정',
        '21 CFR 1 Subpart L에 규정됨'
      ],
      relatedTerms: ['HACCP', 'CGMP', 'Preventive Controls'],
      cfrReference: '21 CFR 1 Subpart L'
    },
    'GRAS': {
      fullName: 'Generally Recognized as Safe',
      koreanName: '일반적으로 안전하다고 인정되는 물질',
      description: '식품 첨가물이나 식품 접촉 물질이 전문가들에 의해 일반적으로 안전하다고 인정되는 상태를 의미합니다.',
      details: [
        'FDA 승인 없이도 사용 가능한 물질',
        '과학적 증거와 전문가 의견에 기반',
        '식품 첨가물 규정(21 CFR 170)에 따라 관리',
        '새로운 용도 사용 시 FDA에 통지 필요'
      ],
      relatedTerms: ['Food Additive', 'Food Contact Substance', 'FDA Notification'],
      cfrReference: '21 CFR 170'
    },
    'RPM': {
      fullName: 'Regulatory Procedures Manual',
      koreanName: '규제 절차 매뉴얼',
      description: 'FDA가 규제 활동을 수행할 때 따라야 하는 내부 절차와 가이드라인을 담은 매뉴얼입니다.',
      details: [
        'FDA 직원을 위한 내부 운영 지침',
        '규제 조치의 일관성과 효율성 보장',
        '검사, 시행, 규제 결정 과정 설명',
        '공개 문서로 누구나 접근 가능'
      ],
      relatedTerms: ['FDA Inspection', 'Enforcement', 'Compliance'],
      cfrReference: 'FDA RPM'
    },
    'GWPE': {
      fullName: 'Good Warehousing Practices for Export',
      koreanName: '수출용 양호한 창고 관리 기준',
      description: '수출용 식품의 창고 보관, 취급, 운송 과정에서 식품 안전을 보장하기 위한 관리 기준입니다.',
      details: [
        '창고 환경 관리 (온도, 습도, 청결도)',
        '식품 보관 및 취급 절차',
        '해충 및 오염 방지 조치',
        '추적 가능성 확보'
      ],
      relatedTerms: ['HACCP', 'CGMP', 'Food Safety'],
      cfrReference: '21 CFR 110'
    },
    'HACCP': {
      fullName: 'Hazard Analysis and Critical Control Points',
      koreanName: '위해요소 분석 및 중요관리점',
      description: '식품 안전을 보장하기 위해 위해요소를 분석하고 중요관리점에서 이를 통제하는 체계적인 접근법입니다.',
      details: [
        '7가지 원칙에 기반한 식품 안전 관리',
        '위해요소 분석 및 예방 조치',
        '중요관리점(CCP) 설정 및 모니터링',
        '21 CFR 117에 규정된 예방관리 요구사항'
      ],
      relatedTerms: ['FSVP', 'CGMP', 'Preventive Controls'],
      cfrReference: '21 CFR 117'
    },
    'CGMP': {
      fullName: 'Current Good Manufacturing Practice',
      koreanName: '현행 우수 제조 기준',
      description: '식품 제조, 포장, 보관 과정에서 식품 안전과 품질을 보장하기 위한 최소한의 요구사항입니다.',
      details: [
        '설비, 공정, 관리 시스템의 기준',
        '직원 교육 및 위생 관리',
        '설비 청소 및 유지보수',
        '21 CFR 110에 규정됨'
      ],
      relatedTerms: ['HACCP', 'FSVP', 'Food Safety'],
      cfrReference: '21 CFR 110'
    }
  };

  const termData = termDatabase[term];
  
  if (!termData) {
    return children;
  }

  const handleMouseEnter = () => {
    setShowTooltip(true);
  };

  const handleMouseLeave = () => {
    setShowTooltip(false);
  };

  const handleClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setShowPopup(true);
  };

  const closePopup = () => {
    setShowPopup(false);
  };

  return (
    <>
      <span
        className={`relative inline-block cursor-pointer text-indigo-600 font-medium hover:text-indigo-800 transition-colors ${className}`}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
      >
        {term}
        
        {/* 간단한 툴팁 */}
        {showTooltip && (
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg shadow-lg z-50 whitespace-nowrap">
            <div className="font-semibold">{termData.koreanName}</div>
            <div className="text-xs text-gray-300 mt-1">{termData.fullName}</div>
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
          </div>
        )}
      </span>

      {/* 상세 팝업 */}
      {showPopup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            {/* 헤더 */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div>
                <h3 className="text-xl font-bold text-gray-900">{term}</h3>
                <p className="text-gray-600 mt-1">{termData.fullName}</p>
                <p className="text-indigo-600 font-medium">{termData.koreanName}</p>
              </div>
              <button
                onClick={closePopup}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* 내용 */}
            <div className="p-6 space-y-6">
              {/* 설명 */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">설명</h4>
                <p className="text-gray-700 leading-relaxed">{termData.description}</p>
              </div>

              {/* 상세 내용 */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">주요 내용</h4>
                <ul className="space-y-2">
                  {termData.details.map((detail, index) => (
                    <li key={index} className="flex items-start">
                      <span className="w-2 h-2 bg-indigo-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                      <span className="text-gray-700">{detail}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* 관련 용어 */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">관련 용어</h4>
                <div className="flex flex-wrap gap-2">
                  {termData.relatedTerms.map((relatedTerm, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm"
                    >
                      {relatedTerm}
                    </span>
                  ))}
                </div>
              </div>

              {/* CFR 참조 */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">규정 참조</h4>
                <div className="flex items-center gap-2">
                  <span className="text-gray-700">{termData.cfrReference}</span>
                  <button className="p-1 hover:bg-gray-200 rounded transition-colors">
                    <ExternalLink className="w-4 h-4 text-indigo-600" />
                  </button>
                </div>
              </div>
            </div>

            {/* 푸터 */}
            <div className="p-6 border-t border-gray-200 bg-gray-50 rounded-b-xl">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Info className="w-4 h-4" />
                <span>더 자세한 정보가 필요하시면 질문해주세요!</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default TermTooltip;
