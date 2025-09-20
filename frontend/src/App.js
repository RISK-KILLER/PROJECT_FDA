// frontend/src/App.js
import React, { useState, useRef, useEffect } from 'react';
import Sidebar from './components/Sidebar.jsx';
import MessageList from './components/MessageList.jsx';
import InputBar from './components/InputBar.jsx';
import HelpModal from './components/HelpModal.jsx';
import { Lightbulb } from 'lucide-react';
import './App.css';

const FDAChatbot = () => {
  
  
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
  const chatAreaRef = useRef(null);

  const currentProject = projects.find(p => p.active);
  
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
      const apiUrl = `${process.env.REACT_APP_API_URL}/api/chat`;

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
        <div className="p-6 border-b border-gray-200 bg-white/80">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
            <p className="text-sm text-gray-600 leading-relaxed">
                  FDA 공식 문서를 바탕으로 정확한 정보를 제공합니다.
                </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowHelpModal(true)}
                className="flex items-center gap-2 bg-yellow-50 hover:bg-yellow-100 text-yellow-700 px-4 py-2 rounded-lg border border-yellow-200 hover:border-yellow-300 transition-colors"
              >
                <Lightbulb className="w-4 h-4" />
                <span className="text-sm font-medium">질문이 어려우신가요? 도움말 보기</span>
              </button>
            </div>
          </div>
        </div>

          {/* 중앙 환영 영역 */}
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center max-w-2xl mx-auto">
              <h2 className="text-3xl font-bold text-gray-800 mb-4">
                {getGreeting()}
              </h2>
              <p className="text-gray-600 text-lg mb-8">FDA 식품 수출 규제에 대해 무엇이든 물어보세요</p>
              
              {/* 중앙 입력창 */}
              <div className="max-w-2xl mx-auto">
                <InputBar
                  inputMessage={inputMessage}
                  setInputMessage={setInputMessage}
                  isTyping={isGenerating}
                  onSend={sendMessage}
                  onKeyPress={handleKeyPress}
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
        <div className="p-6 border-b border-gray-200 bg-white/80">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              {currentProject ? (
                <div className="flex items-center gap-2">
                  <h1 className="text-xl font-semibold text-gray-800">{currentProject.name}</h1>
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
                <h1 className="text-xl font-semibold text-gray-800">FDA Export Assistant</h1>
              )}
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowHelpModal(true)}
                className="flex items-center gap-2 bg-yellow-50 hover:bg-yellow-100 text-yellow-700 px-4 py-2 rounded-lg border border-yellow-200 hover:border-yellow-300 transition-colors"
              >
                <Lightbulb className="w-4 h-4" />
                <span className="text-sm font-medium">질문이 어려우신가요? 도움말 보기</span>
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
    <div className="flex h-screen bg-gradient-to-br from-indigo-50 via-gray-50 to-indigo-50">
      {/* 사이드바 */}
      <Sidebar
        projects={projects}
        onCreateProject={createNewProject}
        onSelectProject={selectProject}
        onDeleteProject={deleteProject}
      />

      {/* 메인 컨텐츠 - 가운데 정렬 */}
      <div className="flex-1 flex justify-center">
        <div className="w-full max-w-4xl flex flex-col bg-white/95 backdrop-blur-sm">
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