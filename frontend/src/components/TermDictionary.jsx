import React, { useState } from 'react';
import { Search, BookOpen, ExternalLink } from 'lucide-react';
import TermTooltip from './TermTooltip';

const TermDictionary = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // FDA 용어 데이터베이스 (카테고리별로 정리)
  const termDatabase = {
    'all': {
      'FSVP': {
        fullName: 'Foreign Supplier Verification Programs',
        koreanName: '해외 공급자 검증 프로그램',
        category: '수입 규제',
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
        category: '식품 첨가물',
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
        category: 'FDA 운영',
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
        category: '창고 관리',
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
        category: '식품 안전',
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
        category: '제조 기준',
        description: '식품 제조, 포장, 보관 과정에서 식품 안전과 품질을 보장하기 위한 최소한의 요구사항입니다.',
        details: [
          '설비, 공정, 관리 시스템의 기준',
          '직원 교육 및 위생 관리',
          '설비 청소 및 유지보수',
          '21 CFR 110에 규정됨'
        ],
        relatedTerms: ['HACCP', 'FSVP', 'Food Safety'],
        cfrReference: '21 CFR 110'
      },
      'FDA': {
        fullName: 'Food and Drug Administration',
        koreanName: '식품의약국',
        category: '정부 기관',
        description: '미국 보건복지부 산하의 식품, 의약품, 의료기기, 화장품 등을 규제하는 연방 기관입니다.',
        details: [
          '식품 안전 및 영양 규제',
          '의약품 및 의료기기 승인',
          '화장품 및 담배 제품 규제',
          '공중보건 보호 및 촉진'
        ],
        relatedTerms: ['CFR', 'Regulation', 'Compliance'],
        cfrReference: 'FDA.gov'
      },
      'CFR': {
        fullName: 'Code of Federal Regulations',
        koreanName: '연방 규정 코드',
        category: '법규',
        description: '미국 연방 정부의 행정 기관들이 발행한 규정들을 체계적으로 정리한 법전입니다.',
        details: [
          '50개 제목으로 구성된 규정 모음',
          '식품 관련 규정은 21 CFR',
          '매년 업데이트되는 살아있는 문서',
          '법적 구속력을 가진 규정'
        ],
        relatedTerms: ['FDA', 'Regulation', 'Compliance'],
        cfrReference: 'ecfr.gov'
      }
    }
  };

  const categories = [
    { id: 'all', name: '전체', count: Object.keys(termDatabase.all).length },
    { id: '수입 규제', name: '수입 규제', count: 1 },
    { id: '식품 첨가물', name: '식품 첨가물', count: 1 },
    { id: 'FDA 운영', name: 'FDA 운영', count: 1 },
    { id: '창고 관리', name: '창고 관리', count: 1 },
    { id: '식품 안전', name: '식품 안전', count: 1 },
    { id: '제조 기준', name: '제조 기준', count: 1 },
    { id: '정부 기관', name: '정부 기관', count: 1 },
    { id: '법규', name: '법규', count: 1 }
  ];

  // 검색 및 필터링된 용어 목록
  const filteredTerms = Object.entries(termDatabase.all).filter(([key, term]) => {
    const matchesSearch = searchTerm === '' || 
      key.toLowerCase().includes(searchTerm.toLowerCase()) ||
      term.koreanName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      term.fullName.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = selectedCategory === 'all' || term.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center gap-2 mb-6">
        <BookOpen className="w-5 h-5 text-indigo-600" />
        <h2 className="text-lg font-semibold text-gray-800">FDA 용어 사전</h2>
      </div>

      {/* 검색 바 */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="용어 검색..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>

      {/* 카테고리 필터 */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">카테고리</h3>
        <div className="flex flex-wrap gap-2">
          {categories.map(category => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-3 py-1 text-xs rounded-full transition-colors ${
                selectedCategory === category.id
                  ? 'bg-indigo-100 text-indigo-700 border border-indigo-200'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {category.name} ({category.count})
            </button>
          ))}
        </div>
      </div>

      {/* 용어 목록 */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {filteredTerms.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <BookOpen className="w-8 h-8 mx-auto mb-2 text-gray-300" />
            <p>검색 결과가 없습니다.</p>
          </div>
        ) : (
          filteredTerms.map(([key, term]) => (
            <div key={key} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <TermTooltip term={key}>
                      <span className="font-semibold text-indigo-600 hover:text-indigo-800 cursor-pointer">
                        {key}
                      </span>
                    </TermTooltip>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                      {term.category}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 font-medium mb-1">{term.koreanName}</p>
                  <p className="text-xs text-gray-500 mb-2">{term.fullName}</p>
                  <p className="text-sm text-gray-600 line-clamp-2">{term.description}</p>
                </div>
                <button className="ml-2 p-1 text-gray-400 hover:text-indigo-600 transition-colors">
                  <ExternalLink className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* 도움말 */}
      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
        <div className="flex items-start gap-2">
          <BookOpen className="w-4 h-4 text-indigo-600 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-indigo-900 mb-1">사용 팁</h4>
            <ul className="text-xs text-indigo-700 space-y-1">
              <li>• 용어에 마우스를 올리면 간단한 설명이 나타납니다</li>
              <li>• 용어를 클릭하면 상세한 정보를 볼 수 있습니다</li>
              <li>• 채팅에서도 용어가 자동으로 감지되어 툴팁이 표시됩니다</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TermDictionary;
