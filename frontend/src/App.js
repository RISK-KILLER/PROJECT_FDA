// frontend/src/App.js
import React, { useState, useRef, useEffect } from 'react';
import { Upload, Send, Plus, CheckCircle, Clock, Circle, Download, FileText, MessageCircle } from 'lucide-react';
import './App.css';

const FDAChatbot = () => {
  const [projects, setProjects] = useState([
    { id: 1, name: '김치 미국 수출', active: true, progress: 2 },
    { id: 2, name: '라면 FDA 인증', active: false, progress: 1 },
    { id: 3, name: '건조 과일 수출', active: false, progress: 0 }
  ]);

  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'user',
      content: '김치 수출하려고 하는데 어떤 규제 확인해야 하나요?'
    },
    {
      id: 2,
      type: 'bot',
      content: '김치는 발효식품으로 분류되어 다음과 같은 FDA 규제를 확인해야 합니다:',
      keywords: ['fermented', 'acidified', 'vegetable', 'low-acid'],
      cfr_references: [
        {
          title: '21 CFR 114 - Acidified Foods',
          description: '산성화 식품에 대한 제조, 가공, 포장 요구사항을 규정합니다. 김치는 pH 4.6 이하의 산성화 식품으로 분류됩니다.'
        },
        {
          title: '21 CFR 108.25 - Emergency Permit Control',
          description: '산성화 식품 제조업체는 FDA에 사전 등록이 필요합니다.'
        }
      ]
    }
  ]);

  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);
  const chatAreaRef = useRef(null);

  const currentProject = projects.find(p => p.active);
  
  const progressSteps = [
    { label: '기본 규제 확인', icon: CheckCircle },
    { label: '인증서 분석', icon: Clock },
    { label: '서류 준비', icon: Circle },
    { label: '최종 체크리스트', icon: Circle }
  ];

  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const createNewProject = () => {
    const projectName = prompt('새 프로젝트 이름을 입력하세요:');
    if (projectName) {
      const newProject = {
        id: Date.now(),
        name: projectName,
        active: true,
        progress: 0
      };
      
      setProjects(prev => prev.map(p => ({ ...p, active: false })).concat(newProject));
      setMessages([]);
    }
  };

  const selectProject = (projectId) => {
    setProjects(prev => prev.map(p => ({ ...p, active: p.id === projectId })));
  };

  // API 호출 함수
// frontend/src/App.js

// API 호출 함수
const callChatAPI = async (message) => {
  try {
    // ✅ 수정된 부분: 환경 변수를 사용하여 백엔드의 전체 URL을 만듭니다.
    const apiUrl = `${process.env.REACT_APP_API_URL}/api/chat`;

    // ✅ 수정된 부분: 완성된 apiUrl 변수를 사용합니다.
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        project_id: currentProject?.id
      }),
    });

    if (!response.ok) {
      // 서버로부터 받은 에러 메시지를 포함하여 오류를 throw합니다.
      const errorData = await response.json().catch(() => ({ detail: 'Unknown server error' }));
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.detail}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API 호출 오류:', error);
    // 오류 시 기본 응답 반환
    return {
      content: `죄송합니다. 서버 연결에 문제가 있습니다. 잠시 후 다시 시도해주세요.\n(에러: ${error.message})`,
      keywords: [],
      cfr_references: [],
      sources: []
    };
  }
};

  const sendMessage = async () => {
    const message = inputMessage.trim();
    if (!message) return;

    const newUserMessage = {
      id: Date.now(),
      type: 'user',
      content: message
    };

    setMessages(prev => [...prev, newUserMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      // 실제 API 호출
      const apiResponse = await callChatAPI(message);
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: apiResponse.content,
        keywords: apiResponse.keywords || [],
        cfr_references: apiResponse.cfr_references || [],
        sources: apiResponse.sources || []
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('메시지 전송 오류:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: '죄송합니다. 응답을 생성하는데 문제가 발생했습니다.',
        keywords: [],
        cfr_references: []
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleFileUpload = (files) => {
    Array.from(files).forEach(file => {
      const uploadMessage = {
        id: Date.now() + Math.random(),
        type: 'user',
        content: `📎 파일 업로드됨: ${file.name}`,
        isFile: true
      };
      setMessages(prev => [...prev, uploadMessage]);

      // TODO: 실제 파일 업로드 API 구현 필요
      setTimeout(() => {
        const analysisMessage = {
          id: Date.now() + Math.random(),
          type: 'bot',
          content: `업로드해주신 "${file.name}" 문서를 분석했습니다:`,
          cfr_references: [
            {
              title: '문서 분석 결과',
              description: '해당 인증서는 FDA 요구사항에 부합하는지 검토했습니다. 파일 분석 기능은 현재 개발 중입니다.'
            }
          ]
        };
        setMessages(prev => [...prev, analysisMessage]);
      }, 1500);
    });
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFileUpload(e.dataTransfer.files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const ProgressIcon = ({ step, index }) => {
    if (index < currentProject?.progress) {
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    } else if (index === currentProject?.progress) {
      return <Clock className="w-5 h-5 text-amber-500" />;
    } else {
      return <Circle className="w-5 h-5 text-gray-400" />;
    }
  };

  const generateChecklist = () => {
    alert('체크리스트 생성 기능은 개발 중입니다.');
  };

  const downloadReport = () => {
    alert('보고서 다운로드 기능은 개발 중입니다.');
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-indigo-100">
      {/* 사이드바 */}
      <div className="w-80 bg-white/95 backdrop-blur-sm border-r border-gray-200 p-6 flex flex-col">
        <div className="flex items-center mb-8">
          <div className="text-2xl mr-3">🏛️</div>
          <h1 className="text-xl font-bold text-gray-800">FDA Export Assistant</h1>
        </div>

        {/* 프로젝트 섹션 */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">프로젝트</h2>
          <button
            onClick={createNewProject}
            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 px-4 rounded-lg font-medium mb-4 hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 flex items-center justify-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            새 수출 프로젝트
          </button>
          
          <div className="space-y-2">
            {projects.map(project => (
              <div
                key={project.id}
                onClick={() => selectProject(project.id)}
                className={`p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                  project.active 
                    ? 'bg-indigo-50 border-l-4 border-indigo-600 text-indigo-900' 
                    : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                }`}
              >
                {project.name}
              </div>
            ))}
          </div>
        </div>

        {/* 진행 상황 */}
        <div className="flex-1">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">진행 상황</h2>
          <div className="space-y-4">
            {progressSteps.map((step, index) => (
              <div key={index} className="flex items-center">
                <ProgressIcon step={step} index={index} />
                <span className="ml-3 text-sm text-gray-700">{step.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 메인 컨텐츠 */}
      <div className="flex-1 flex flex-col bg-white/95 backdrop-blur-sm">
        {/* 헤더 */}
        <div className="p-6 border-b border-gray-200 bg-white/80">
          <h1 className="text-xl font-semibold text-gray-800">{currentProject?.name}</h1>
          <p className="text-gray-500 text-sm mt-1">FDA 공식 데이터 기반 규제 안내</p>
        </div>

        {/* 채팅 영역 */}
        <div ref={chatAreaRef} className="flex-1 p-6 overflow-y-auto space-y-6">
          {messages.map(message => (
            <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[70%] rounded-2xl px-6 py-4 ${
                message.type === 'user'
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-br-md'
                  : 'bg-gray-50 border border-gray-200 rounded-bl-md'
              }`}>
                <div className="whitespace-pre-wrap">{message.content}</div>
                
                {message.keywords && message.keywords.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-3">
                    {message.keywords.map((keyword, index) => (
                      <span
                        key={index}
                        className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full border border-green-200"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                )}

                {message.cfr_references && message.cfr_references.length > 0 && (
                  <div className="mt-4 space-y-3">
                    {message.cfr_references.map((ref, index) => (
                      <div key={index} className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                        <h4 className="font-semibold text-indigo-900 mb-2">{ref.title}</h4>
                        <p className="text-sm text-indigo-700">{ref.description}</p>
                        {ref.url && (
                          <a href={ref.url} target="_blank" rel="noopener noreferrer" className="text-xs text-indigo-600 hover:underline mt-2 block">
                            원본 문서 보기
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 text-xs text-gray-500">
                    출처: {message.sources.slice(0, 2).join(', ')}
                    {message.sources.length > 2 && ` 외 ${message.sources.length - 2}건`}
                  </div>
                )}

                {message.type === 'bot' && (
                  <div className="flex gap-2 mt-4">
                    <button 
                      onClick={generateChecklist}
                      className="flex items-center gap-1 bg-indigo-100 text-indigo-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-indigo-200 transition-colors"
                    >
                      <FileText className="w-4 h-4" />
                      체크리스트 생성
                    </button>
                    <button 
                      onClick={downloadReport}
                      className="flex items-center gap-1 bg-indigo-100 text-indigo-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-indigo-200 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      보고서 다운로드
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-gray-50 border border-gray-200 rounded-2xl rounded-bl-md px-6 py-4 max-w-[70%]">
                <div className="flex items-center gap-1">
                  <MessageCircle className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-500 italic">AI가 응답을 생성중입니다...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 입력 영역 */}
        <div className="p-6 border-t border-gray-200 bg-white/80">
          {/* 파일 업로드 영역 */}
          <div
            className={`border-2 border-dashed rounded-lg p-6 text-center mb-4 transition-colors cursor-pointer ${
              dragOver 
                ? 'border-indigo-500 bg-indigo-50' 
                : 'border-gray-300 hover:border-indigo-400 hover:bg-indigo-50'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
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
              onChange={(e) => handleFileUpload(e.target.files)}
            />
          </div>

          {/* 메시지 입력 */}
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="추가 질문이나 업로드한 문서에 대해 문의하세요..."
                className="w-full border border-gray-300 rounded-xl px-4 py-3 resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                rows={2}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isTyping}
              className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              전송
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FDAChatbot;
