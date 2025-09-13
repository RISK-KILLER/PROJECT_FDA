// frontend/src/App.js
import React, { useState, useRef, useEffect } from 'react';
import { Upload, Send, Plus, CheckCircle, Clock, Circle, Download, FileText, MessageCircle , X } from 'lucide-react';
import './App.css';

const FDAChatbot = () => {
  const [activeTab, setActiveTab] = useState('regulations');
  
  const [projects, setProjects] = useState([
    { id: 1, name: '김치 미국 수출', active: true, progress: 2 },
  ]);

  // 프로젝트별 메시지를 저장하는 객체
  const [projectMessages, setProjectMessages] = useState({
    1: [  // 기본 프로젝트의 초기 메시지
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
    ]
  });

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);
  const chatAreaRef = useRef(null);

  const currentProject = projects.find(p => p.active);
  
  // 컴포넌트 마운트 시 현재 프로젝트의 메시지 로드
  useEffect(() => {
    if (currentProject) {
      const currentProjectMessages = projectMessages[currentProject.id] || [];
      setMessages(currentProjectMessages);
    }
  }, [currentProject?.id]);

  const progressSteps = [
    { id: 'regulations', label: '기본 규제 확인', icon: CheckCircle },
    { id: 'certificates', label: '인증서 분석', icon: Clock },
    { id: 'documents', label: '서류 준비', icon: Circle },
    { id: 'checklist', label: '최종 체크리스트', icon: Circle }
  ];

  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const createNewProject = () => {
    const projectName = prompt('새 프로젝트 이름을 입력하세요:');
    if (projectName) {
      const newProjectId = Date.now();
      const newProject = {
        id: newProjectId,
        name: projectName,
        active: true,
        progress: 0
      };
      
      // 현재 메시지를 현재 프로젝트에 저장
      if (currentProject) {
        setProjectMessages(prev => ({
          ...prev,
          [currentProject.id]: messages
        }));
      }
      
      // 새 프로젝트 추가
      setProjects(prev => prev.map(p => ({ ...p, active: false })).concat(newProject));
      
      // 새 프로젝트의 빈 메시지 배열 생성
      setProjectMessages(prev => ({
        ...prev,
        [newProjectId]: []
      }));
      
      // 현재 화면 메시지를 빈 배열로 설정
      setMessages([]);
    }
  };

  const selectProject = (projectId) => {
    // 현재 메시지를 현재 프로젝트에 저장
    if (currentProject) {
      setProjectMessages(prev => ({
        ...prev,
        [currentProject.id]: messages
      }));
    }
    
    // 프로젝트 변경
    setProjects(prev => prev.map(p => ({ ...p, active: p.id === projectId })));
    
    // 선택된 프로젝트의 메시지 불러오기
    const selectedProjectMessages = projectMessages[projectId] || [];
    setMessages(selectedProjectMessages);
  };

  // API 호출 함수
  const callChatAPI = async (message) => {
    try {
      const apiUrl = `${process.env.REACT_APP_API_URL}/api/chat`;

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
        const errorData = await response.json().catch(() => ({ detail: 'Unknown server error' }));
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.detail}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API 호출 오류:', error);
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

    const updatedMessages = [...messages, newUserMessage];
    setMessages(updatedMessages);
    
    // 현재 프로젝트의 메시지도 업데이트
    setProjectMessages(prev => ({
      ...prev,
      [currentProject.id]: updatedMessages
    }));
    
    setInputMessage('');
    setIsTyping(true);

    try {
      const apiResponse = await callChatAPI(message);
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: apiResponse.content,
        keywords: apiResponse.keywords || [],
        cfr_references: apiResponse.cfr_references || [],
        sources: apiResponse.sources || []
      };
      
      const finalMessages = [...updatedMessages, botMessage];
      setMessages(finalMessages);
      
      // 프로젝트 메시지도 업데이트
      setProjectMessages(prev => ({
        ...prev,
        [currentProject.id]: finalMessages
      }));
      
    } catch (error) {
      console.error('메시지 전송 오류:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: '죄송합니다. 응답을 생성하는데 문제가 발생했습니다.',
        keywords: [],
        cfr_references: []
      };
      const finalMessages = [...updatedMessages, errorMessage];
      setMessages(finalMessages);
      
      // 프로젝트 메시지도 업데이트
      setProjectMessages(prev => ({
        ...prev,
        [currentProject.id]: finalMessages
      }));
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

  const resetConversation = async () => {
    if (window.confirm('현재 대화를 초기화하시겠습니까?')) {
      try {
        await fetch(`${process.env.REACT_APP_API_URL}/api/project/${currentProject.id}/reset`, {
          method: 'POST',
        });
        setMessages([]);
        // 프로젝트 메시지도 초기화
        setProjectMessages(prev => ({
          ...prev,
          [currentProject.id]: []
        }));
      } catch (error) {
        console.error('대화 초기화 API 호출 오류:', error);
      }
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
      const updatedMessages = [...messages, uploadMessage];
      setMessages(updatedMessages);
      
      // 프로젝트 메시지도 업데이트
      setProjectMessages(prev => ({
        ...prev,
        [currentProject.id]: updatedMessages
      }));

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
        const finalMessages = [...updatedMessages, analysisMessage];
        setMessages(finalMessages);
        
        // 프로젝트 메시지도 업데이트
        setProjectMessages(prev => ({
          ...prev,
          [currentProject.id]: finalMessages
        }));
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

  // 채팅 컨텐츠 렌더링
  const renderChatContent = () => (
    <>
      {/* 헤더 */}
      <div className="p-6 border-b border-gray-200 bg-white/80">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-xl font-semibold text-gray-800">{currentProject?.name}</h1>
            <p className="text-gray-500 text-sm mt-1">FDA 공식 데이터 기반 규제 안내</p>
          </div>
          <button
            onClick={resetConversation}
            className="text-gray-500 hover:text-gray-700 text-sm px-3 py-1 rounded border border-gray-300 hover:border-gray-400 transition-colors"
          >
            대화 초기화
          </button>
        </div>
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
    </>
  );

  const deleteProject = async (projectId) => {
    if (projects.length <= 1) {
      alert('최소 하나의 프로젝트는 유지되어야 합니다.');
      return;
    }
    
    if (window.confirm('정말 이 프로젝트를 삭제하시겠습니까?')) {
      try {
        await fetch(`${process.env.REACT_APP_API_URL}/api/project/${projectId}`, {
          method: 'DELETE',
        });
      } catch (error) {
        console.error('프로젝트 삭제 API 호출 오류:', error);
      }
      
      const deletingActiveProject = projects.find(p => p.id === projectId)?.active;
      
      // 프로젝트 메시지도 함께 삭제
      setProjectMessages(prev => {
        const newMessages = { ...prev };
        delete newMessages[projectId];
        return newMessages;
      });
      
      setProjects(prev => {
        const remaining = prev.filter(p => p.id !== projectId);
        
        if (deletingActiveProject && remaining.length > 0) {
          remaining[0].active = true;
          // 첫 번째 남은 프로젝트의 메시지 불러오기
          const firstProjectMessages = projectMessages[remaining[0].id] || [];
          setMessages(firstProjectMessages);
        }
        
        return remaining;
      });
    }
  };

  // 탭별 컨텐츠 렌더링
  const renderTabContent = () => {
    switch (activeTab) {
      case 'regulations':
        return renderChatContent();
      case 'certificates':
        return (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-700 mb-2">인증서 분석</h3>
              <p className="text-gray-500">업로드된 인증서를 분석하는 기능이 곧 추가됩니다.</p>
            </div>
          </div>
        );
      case 'documents':
        return (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <Upload className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-700 mb-2">서류 준비</h3>
              <p className="text-gray-500">필요한 서류를 준비하고 관리하는 기능이 곧 추가됩니다.</p>
            </div>
          </div>
        );
      case 'checklist':
        return (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <CheckCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-700 mb-2">최종 체크리스트</h3>
              <p className="text-gray-500">수출 전 최종 점검 체크리스트가 곧 추가됩니다.</p>
            </div>
          </div>
        );
      default:
        return renderChatContent();
    }
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
                className={`p-3 rounded-lg transition-all duration-200 ${
                  project.active 
                    ? 'bg-indigo-50 border-l-4 border-indigo-600 text-indigo-900' 
                    : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span 
                    onClick={() => selectProject(project.id)}
                    className="flex-1 cursor-pointer"
                  >
                    {project.name}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteProject(project.id);
                    }}
                    className="ml-2 p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                    title="프로젝트 삭제"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 탭 메뉴 */}
        <div className="flex-1">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">작업 단계</h2>
          <div className="space-y-2">
            {progressSteps.map((step, index) => (
              <div
                key={index}
                onClick={() => setActiveTab(step.id)}
                className={`flex items-center p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                  activeTab === step.id 
                    ? 'bg-indigo-100 text-indigo-700 border-l-4 border-indigo-600' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
              >
                <ProgressIcon step={step} index={index} />
                <span className="ml-3 text-sm font-medium">{step.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 메인 컨텐츠 */}
      <div className="flex-1 flex flex-col bg-white/95 backdrop-blur-sm">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default FDAChatbot;