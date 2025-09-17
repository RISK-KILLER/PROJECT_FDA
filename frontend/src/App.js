// frontend/src/App.js
import React, { useState, useRef, useEffect } from 'react';
import Sidebar from './components/Sidebar.jsx';
import MessageList from './components/MessageList.jsx';
import InputBar from './components/InputBar.jsx';
import './App.css';

const FDAChatbot = () => {
  
  
  const [projects, setProjects] = useState([
    { id: 1, name: '김치 미국 수출', active: true, progress: 2 },
  ]);

  // 프로젝트별 메시지를 저장하는 객체
  const [projectMessages, setProjectMessages] = useState({
    1: [  // 기본 프로젝트의 초기 메시지
      {
        id: 1,
        type: 'user',
        content: '아래 내용은 해당 챗봇 이용을 위한 가이드라인입니다.\n새로운 프로젝트를 생성해서 궁금한 내용들을 질문해보세요.'
      },
      {
        id: 2,
        type: 'bot',
        content: '식품 수출을 위한 가이드라인이 필요할 때, 아래와 같은 내용으로 질문해보세요. 원문 링크는 답변과 함께 제공됩니다.',
        keywords: ['quick prompts', 'HACCP', 'FSVP', 'labeling'],
        cfr_references: [
          {
            title: '21 CFR 117 - CGMP, Hazard Analysis, and Risk-Based Preventive Controls',
            description: 'HACCP 유사 체계로 위해요소 분석과 예방관리 요구사항을 규정합니다.',
            url: 'https://www.ecfr.gov/current/title-21/chapter-I/subchapter-B/part-117'
          },
          {
            title: '21 CFR 1 Subpart L - Foreign Supplier Verification Programs (FSVP)',
            description: '미국 수입자의 공급자 검증 의무를 규정합니다.',
            url: 'https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-1/subpart-L'
          },
          {
            title: '21 CFR 101 - Food Labeling',
            description: '영양성분표, 알레르겐, 성분표시 등 라벨링 요구사항을 규정합니다.',
            url: 'https://www.ecfr.gov/current/title-21/chapter-I/subchapter-B/part-101'
          }
        ],
        scenarios: [
          { title: '김치 수출 초기 점검', summary: '규정 범위·핵심 요구사항 빠른 파악', prompt: '김치 미국 수출 초기 점검용으로, 적용 가능한 FDA 규정 범위와 핵심 요구사항을 한 페이지 요약으로 정리해줘.' },
          { title: 'FSVP 준비', summary: '수입자 검증 문서 리스트업', prompt: 'FSVP 준비를 위해 우리 케이스에 필요한 문서·검증 항목을 체크리스트로 만들어줘.' },
          { title: '라벨 검토', summary: '라벨링 적용 항목 추출', prompt: '라벨링(21 CFR 101)에서 우리 제품에 적용되는 항목만 추려서 점검표로 만들어줘.' }
        ],
        samples: [
          { user: '배추·고춧가루·마늘·젓갈 기준으로 알레르겐과 표준명 정규화 도와줘.', bot: '알레르겐(예: 어패류 유래 젓갈) 표시 필요 여부를 확인하고, 성분 표준명을 정리해 드릴게요.' },
          { user: '발효 단계에서 CCP가 될 수 있는 포인트를 알려줘.', bot: '온도·시간·pH를 중심으로 모니터링 항목과 한계기준을 제안합니다.' }
        ]
      }
    ]
  });

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const timerRef = useRef(null);
  const startTimeRef = useRef(null);
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
          project_id: currentProject?.id,
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
    setIsGenerating(true);
    // 타이머 시작
    startTimer();

    try {
      const apiResponse = await callChatAPI(message);
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
        [currentProject.id]: finalMessages
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
        [currentProject.id]: finalMessages
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

  // 채팅 컨텐츠 렌더링
  const renderChatContent = () => (
    <>
      {/* 헤더 */}
      <div className="p-6 border-b border-gray-200 bg-white/80">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-xl font-semibold text-gray-800">{currentProject?.name}</h1>
            <p className="text-gray-500 text-sm mt-1">FDA 공식 문서를 바탕으로 수출 규제를 빠르게 확인하세요</p>
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

  

  return (
    <div className="flex h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-indigo-100">
      {/* 사이드바 */}
      <Sidebar
        projects={projects}
        onCreateProject={createNewProject}
        onSelectProject={selectProject}
        onDeleteProject={deleteProject}
      />

      {/* 메인 컨텐츠 */}
      <div className="flex-1 flex flex-col bg-white/95 backdrop-blur-sm">
        {renderChatContent()}
      </div>
    </div>
  );
};

export default FDAChatbot;