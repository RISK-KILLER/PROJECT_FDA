import React from 'react';
import { X, Lightbulb, MessageSquare } from 'lucide-react';

const HelpModal = ({ isOpen, onClose, onSelectQuestion, onSendMessage }) => {
  if (!isOpen) return null;

  const exampleQuestions = {
    '제품별 질문': [
      { text: '김치 수출 시 라벨링 요구사항', prompt: '김치를 미국으로 수출할 때 라벨링에 필요한 요구사항을 알려주세요.' },
      { text: '라면 수출 시 필요한 첨가물 승인', prompt: '라면을 미국으로 수출할 때 필요한 첨가물 승인 절차를 알려주세요.' },
      { text: '음료 수출 시 영양표시 방법', prompt: '음료를 미국으로 수출할 때 영양표시는 어떻게 해야 하나요?' },
      { text: '냉동식품 수출 규정', prompt: '냉동식품을 미국으로 수출할 때 준수해야 할 규정을 알려주세요.' },
      { text: '건강기능식품 수출 조건', prompt: '건강기능식품을 미국으로 수출할 때 필요한 조건과 승인 절차를 알려주세요.' }
    ],
    '규제별 질문': [
      { text: '알러지 유발요소 표시 방법', prompt: '식품 라벨에 알러지 유발요소는 어떻게 표시해야 하나요?' },
      { text: 'FSVP 준비 절차', prompt: 'FSVP(Foreign Supplier Verification Programs) 준비 절차를 단계별로 알려주세요.' },
      { text: 'GRAS 승인 첨가물 목록', prompt: 'GRAS로 승인된 첨가물 목록을 확인할 수 있나요?' },
      { text: '영양성분표 작성법', prompt: 'FDA 요구사항에 맞는 영양성분표는 어떻게 작성하나요?' },
      { text: 'FDA 시설 등록 방법', prompt: 'FDA에 시설을 등록하는 방법과 필요한 서류를 알려주세요.' }
    ],
    '문제해결': [
      { text: '리콜 예방 방법', prompt: '식품 리콜을 예방하기 위한 방법과 체크리스트를 알려주세요.' },
      { text: '라벨 거부 사유', prompt: 'FDA에서 라벨을 거부하는 주요 사유와 해결 방법을 알려주세요.' },
      { text: '통관 지연 해결', prompt: '미국 통관이 지연될 때 해결 방법과 대응 절차를 알려주세요.' },
      { text: '검사 대비 방법', prompt: 'FDA 검사에 대비하는 방법과 준비사항을 알려주세요.' }
    ]
  };

  const handleQuestionClick = (question) => {
    onSelectQuestion(question.prompt);
    onClose();
    // 자동으로 질문 전송
    setTimeout(() => {
      onSendMessage();
    }, 100);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-y-auto">
        {/* 헤더 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Lightbulb className="w-6 h-6 text-yellow-500" />
            <h2 className="text-xl font-bold text-gray-900">질문이 어려우신가요? 도움말 보기</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* 컨텐츠 */}
        <div className="p-6">
          <div className="text-center mb-8">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">이런 질문을 해보세요:</h3>
            <p className="text-gray-600">아래 예시 질문을 클릭하면 바로 질문할 수 있습니다.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {Object.entries(exampleQuestions).map(([category, questions]) => (
              <div key={category} className="space-y-4">
                <h4 className="text-lg font-semibold text-gray-800 border-b border-gray-200 pb-2">
                  {category}
                </h4>
                <div className="space-y-3">
                  {questions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleQuestionClick(question)}
                      className="w-full text-left p-4 bg-gray-50 hover:bg-indigo-50 border border-gray-200 hover:border-indigo-300 rounded-lg transition-all duration-200 group"
                    >
                      <div className="flex items-start gap-3">
                        <MessageSquare className="w-4 h-4 text-gray-400 group-hover:text-indigo-500 mt-1 flex-shrink-0" />
                        <span className="text-sm text-gray-700 group-hover:text-indigo-700 font-medium">
                          {question.text}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* 추가 도움말 */}
          <div className="mt-8 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
            <div className="flex items-start gap-3">
              <Lightbulb className="w-5 h-5 text-indigo-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-indigo-900 mb-2">사용 팁</h4>
                <ul className="text-sm text-indigo-700 space-y-1">
                  <li>• 구체적인 제품명과 상황을 포함해서 질문하세요</li>
                  <li>• FDA 용어에 마우스를 올리면 간단한 설명을 볼 수 있습니다</li>
                  <li>• 사이드바의 용어사전에서 더 많은 정보를 확인할 수 있습니다</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HelpModal;
