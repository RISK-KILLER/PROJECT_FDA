// frontend/src/App.js
import React, { useState, useRef, useEffect } from 'react';
import Sidebar from './components/Sidebar.jsx';
import MessageList from './components/MessageList.jsx';
import InputBar from './components/InputBar.jsx';
import HelpModal from './components/HelpModal.jsx';
import { Lightbulb } from 'lucide-react';
import './App.css';

const FDAChatbot = () => {
  // PWA 상태 관리
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  
  const [projects, setProjects] = useState([]);

  // 프로젝트별 메시지를 저장하는 객체 (초기 메시지 제거)
  const [projectMessages, setProjectMessages] = useState({});

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const timerRef = useRef(null);
  const startTimeRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);
  const chatAreaRef = useRef(null);

  const currentProject = projects.find(p => p.active);
  
  // PWA Service Worker 등록 및 설치 프롬프트 처리
  useEffect(() => {
    // Service Worker 등록
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(registration => {
          console.log('Service Worker registered successfully:', registration);
        })
        .catch(error => {
          console.log('Service Worker registration failed:', error);
        });
    }

    // 설치 프롬프트 이벤트 리스너
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstallPrompt(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // 온라인/오프라인 상태 감지
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // 프로젝트가 변경될 때마다 메시지 로드
  useEffect(() => {
    if (currentProject) {
      const currentProjectMessages = projectMessages[currentProject.id] || [];
      setMessages(currentProjectMessages);
    } else {
      setMessages([]);
    }
  }, [currentProject?.id, projects]);

  

  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // 타이머 함수들
  const startTimer = () => {
    startTimeRef.current = Date.now();
    setElapsedTime(0);
    timerRef.current = setInterval(() => {
      setElapsedTime(Date.now() - startTimeRef.current);
    }, 100);
  };

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  // PWA 설치 함수
  const handleInstallApp = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      console.log(`PWA 설치 결과: ${outcome}`);
      setDeferredPrompt(null);
      setShowInstallPrompt(false);
    }
  };

  // 오프라인 상태에서 메시지 전송 시 처리
  const handleOfflineMessage = () => {
    const offlineMessage = {
      id: Date.now(),
      type: 'assistant',
      content: '현재 오프라인 상태입니다. 네트워크 연결을 확인해주세요.',
      timestamp: new Date().toISOString(),
      offline: true
    };
    setMessages(prev => [...prev, offlineMessage]);
  };

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
      
      // 현재 메시지를 현재 프로젝트에 저장 (현재 프로젝트가 있는 경우에만)
      if (currentProject) {
        setProjectMessages(prev => ({
          ...prev,
          [currentProject.id]: messages
        }));
      }
      
      // 새 프로젝트 추가 (기존 프로젝트가 있으면 비활성화)
      setProjects(prev => {
        const updatedProjects = prev.map(p => ({ ...p, active: false }));
        return [...updatedProjects, newProject];
      });
      
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
  const callChatAPI = async (message, projectId) => {
    try {
      // 모바일에서도 접속 가능하도록 IP 주소 사용
      const getApiUrl = () => {
        if (process.env.REACT_APP_API_URL) {
          return process.env.REACT_APP_API_URL;
        }
        
        // 모바일에서 접속할 때는 컴퓨터의 IP 주소 사용
        const hostname = window.location.hostname;
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
          return 'http://localhost:8000';
        } else {
          // 모바일에서 접속할 때는 같은 IP 주소의 8000 포트 사용
          return `http://${hostname}:8000`;
        }
      };
      
      const apiUrl = `${getApiUrl()}/api/chat`;
      console.log('API URL:', apiUrl); // 디버깅용

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          project_id: projectId,
          language: 'ko'
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

    // 오프라인 상태 체크
    if (!isOnline) {
      handleOfflineMessage();
      return;
    }

    // 프로젝트가 없으면 자동으로 생성
    let activeProject = currentProject;
    if (!activeProject) {
      const now = new Date();
      const timeString = now.toLocaleTimeString('ko-KR', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      });
      const projectName = `FDA 수출 문의 ${timeString}`;
      const newProjectId = Date.now();
      const newProject = {
        id: newProjectId,
        name: projectName,
        active: true,
        progress: 0
      };
      
      setProjects([newProject]);
      setProjectMessages(prev => ({
        ...prev,
        [newProjectId]: []
      }));
      activeProject = newProject;
    }

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
      [activeProject.id]: updatedMessages
    }));
    
    setInputMessage('');
    setIsGenerating(true);
    // 타이머 시작
    startTimer();

    try {
      const apiResponse = await callChatAPI(message, activeProject.id);
      // 타이머 정지
      stopTimer();
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: apiResponse.content,
        keywords: apiResponse.keywords || [],
        cfr_references: apiResponse.cfr_references || [],
        sources: apiResponse.sources || [],
        responseTime: apiResponse.responseTime || elapsedTime,
        agentResponseTime: apiResponse.agentResponseTime,
        timestamp: apiResponse.timestamp
      };
      
      const finalMessages = [...updatedMessages, botMessage];
      setMessages(finalMessages);
      
      // 프로젝트 메시지도 업데이트
      setProjectMessages(prev => ({
        ...prev,
        [activeProject.id]: finalMessages
      }));
      
    } catch (error) {
      stopTimer();
      console.error('메시지 전송 오류:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: '죄송합니다. 응답을 생성하는데 문제가 발생했습니다.',
        keywords: [],
        cfr_references: [],
        responseTime: elapsedTime
      };
      const finalMessages = [...updatedMessages, errorMessage];
      setMessages(finalMessages);
      
      // 프로젝트 메시지도 업데이트
      setProjectMessages(prev => ({
        ...prev,
        [activeProject.id]: finalMessages
      }));
    } finally {
      setIsGenerating(false);
    }
  };

  // 컴포넌트 언마운트 시 타이머 정리
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

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

  

  const generateChecklist = () => {
    alert('체크리스트 생성 기능은 개발 중입니다.');
  };

  const downloadReport = () => {
    alert('보고서 다운로드 기능은 개발 중입니다.');
  };

  // 도움말에서 질문 선택 시 처리
  const handleHelpQuestionSelect = (question) => {
    setInputMessage(question);
    setShowHelpModal(false);
  };

  // 시간대별 인사말 생성
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 6) {
      return "좋은 새벽이에요, 사용자님";
    } else if (hour < 12) {
      return "좋은 아침이에요, 사용자님";
    } else if (hour < 18) {
      return "좋은 오후에요, 사용자님";
    } else {
      return "좋은 저녁이에요, 사용자님";
    }
  };

  // 채팅 컨텐츠 렌더링
  const renderChatContent = () => {
    // 메시지가 없을 때는 클로드 스타일의 중앙 레이아웃
    if (messages.length === 0) {
      return (
        <>
        {/* 헤더 */}
        <div className="p-3 lg:p-6 border-b border-purple-100 bg-purple-50/30">
          <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center gap-3">
            <div className="flex items-center gap-3">
              <p className="text-xs lg:text-sm text-gray-600 leading-relaxed">
                FDA 공식 문서를 바탕으로 정확한 정보를 제공합니다.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowHelpModal(true)}
                className="flex items-center gap-2 bg-yellow-50 hover:bg-yellow-100 text-yellow-700 px-3 lg:px-4 py-2 rounded-lg border border-yellow-200 hover:border-yellow-300 transition-colors"
              >
                <Lightbulb className="w-4 h-4" />
                <span className="text-xs lg:text-sm font-medium">질문이 어려우신가요? 도움말 보기</span>
              </button>
            </div>
          </div>
        </div>

          {/* 중앙 환영 영역 */}
          <div className="flex-1 flex items-center justify-center p-3 lg:p-6">
            <div className="text-center max-w-2xl mx-auto">
              <h2 className="text-2xl lg:text-3xl font-bold text-gray-800 mb-3 lg:mb-4">
                {getGreeting()}
              </h2>
              <p className="text-gray-600 text-base lg:text-lg mb-6 lg:mb-8">FDA 식품 수출 규제에 대해 무엇이든 물어보세요</p>
              
              {/* 중앙 입력창 */}
              <div className="max-w-2xl mx-auto">
                <InputBar
                  inputMessage={inputMessage}
                  setInputMessage={setInputMessage}
                  isTyping={isGenerating}
                  onSend={sendMessage}
                  onKeyPress={handleKeyPress}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  dragOver={dragOver}
                  fileInputRef={fileInputRef}
                  onFileChange={(e) => handleFileUpload(e.target.files)}
                  isCentered={true}
                />
              </div>
            </div>
          </div>
        </>
      );
    }

    // 메시지가 있을 때는 일반 채팅 레이아웃
    return (
      <>
        {/* 헤더 */}
        <div className="p-3 lg:p-6 border-b border-purple-100 bg-purple-50/30">
          <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center gap-3">
            <div className="flex items-center gap-3">
              {currentProject ? (
                <div className="flex items-center gap-2">
                  <h1 className="text-lg lg:text-xl font-semibold text-gray-800">{currentProject.name}</h1>
                  <button
                    onClick={() => {
                      const newName = prompt('프로젝트 이름을 변경하세요:', currentProject.name);
                      if (newName && newName.trim()) {
                        console.log('프로젝트 이름 변경:', currentProject.name, '->', newName.trim());
                        setProjects(prev => prev.map(p => 
                          p.id === currentProject.id ? { ...p, name: newName.trim() } : p
                        ));
                      }
                    }}
                    className="text-gray-400 hover:text-gray-600 text-sm px-2 py-1 rounded hover:bg-gray-100 transition-colors"
                    title="프로젝트 이름 변경"
                  >
                    ✏️
                  </button>
                </div>
              ) : (
                <h1 className="text-lg lg:text-xl font-semibold text-gray-800">FDA Export Assistant</h1>
              )}
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowHelpModal(true)}
                className="flex items-center gap-2 bg-yellow-50 hover:bg-yellow-100 text-yellow-700 px-3 lg:px-4 py-2 rounded-lg border border-yellow-200 hover:border-yellow-300 transition-colors"
              >
                <Lightbulb className="w-4 h-4" />
                <span className="text-xs lg:text-sm font-medium">질문이 어려우신가요? 도움말 보기</span>
              </button>
              {currentProject && (
                <button
                  onClick={resetConversation}
                  className="text-gray-500 hover:text-gray-700 text-sm px-3 py-1 rounded border border-gray-300 hover:border-gray-400 transition-colors"
                >
                  대화 초기화
                </button>
              )}
            </div>
          </div>
        </div>


        {/* 채팅 영역 */}
        <div ref={chatAreaRef} className="flex-1 p-0 overflow-y-auto">
          <MessageList
            messages={messages}
            isTyping={isGenerating}
            elapsedTime={elapsedTime}
            onGenerateChecklist={generateChecklist}
            onDownloadReport={downloadReport}
            setInputMessage={setInputMessage}
            sendMessage={sendMessage}
          />
        </div>

        {/* 입력 영역 */}
        <InputBar
          inputMessage={inputMessage}
          setInputMessage={setInputMessage}
          isTyping={isGenerating}
          onSend={sendMessage}
          onKeyPress={handleKeyPress}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          dragOver={dragOver}
          fileInputRef={fileInputRef}
          onFileChange={(e) => handleFileUpload(e.target.files)}
        />
      </>
    );
  };

  const deleteProject = async (projectId) => {
    if (projects.length <= 1) {
      // 마지막 프로젝트를 삭제하면 프로젝트가 없는 상태로 변경
      setProjects([]);
      setMessages([]);
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

  

  return (
    <div className="flex h-screen bg-gradient-to-br from-purple-50/30 via-purple-50/20 to-purple-50/40">
      {/* 오프라인 상태 표시 */}
      {!isOnline && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-red-500 text-white text-center py-2 text-sm">
          📱 오프라인 상태입니다. 일부 기능이 제한될 수 있습니다.
        </div>
      )}

      {/* PWA 설치 프롬프트 */}
      {showInstallPrompt && (
        <div className="fixed top-4 right-4 z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-4 max-w-sm">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                📱
              </div>
            </div>
            <div className="flex-1">
              <h3 className="font-medium text-gray-900 text-sm">앱으로 설치하기</h3>
              <p className="text-gray-600 text-xs mt-1">홈 화면에 추가하여 더 편리하게 사용하세요.</p>
              <div className="flex gap-2 mt-3">
                <button
                  onClick={handleInstallApp}
                  className="bg-indigo-500 text-white px-3 py-1 rounded text-xs hover:bg-indigo-600 transition-colors"
                >
                  설치
                </button>
                <button
                  onClick={() => setShowInstallPrompt(false)}
                  className="text-gray-500 px-3 py-1 rounded text-xs hover:bg-gray-100 transition-colors"
                >
                  나중에
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 사이드바 */}
      <Sidebar
        projects={projects}
        onCreateProject={createNewProject}
        onSelectProject={selectProject}
        onDeleteProject={deleteProject}
      />

      {/* 메인 컨텐츠 - 모바일 최적화 */}
      <div className="flex-1 flex justify-center lg:ml-0 ml-0">
        <div className="w-full max-w-4xl flex flex-col bg-purple-50/20 backdrop-blur-sm">
          {renderChatContent()}
        </div>
      </div>

      {/* 도움말 모달 */}
      <HelpModal
        isOpen={showHelpModal}
        onClose={() => setShowHelpModal(false)}
        onSelectQuestion={handleHelpQuestionSelect}
        onSendMessage={sendMessage}
      />
    </div>
  );
};

export default FDAChatbot;