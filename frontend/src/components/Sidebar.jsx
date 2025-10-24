import React, { useState } from 'react';
import { Plus, X, BookOpen, MessageSquare, Menu } from 'lucide-react';
import TermDictionary from './TermDictionary';

const Sidebar = ({ projects, onCreateProject, onSelectProject, onDeleteProject }) => {
  const [activeTab, setActiveTab] = useState('projects');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <>
      {/* 모바일 메뉴 버튼 */}
      <button
        onClick={() => setIsMobileMenuOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-50 bg-white border border-gray-200 rounded-lg p-2 shadow-lg"
      >
        <Menu className="w-5 h-5 text-gray-600" />
      </button>

      {/* 모바일 오버레이 */}
      {isMobileMenuOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* 사이드바 */}
      <div className={`
        fixed lg:relative lg:translate-x-0 lg:z-auto z-50
        w-72 h-full bg-gray-50 border-r border-gray-200 flex flex-col
        transform transition-transform duration-300 ease-in-out
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* 헤더 */}
        <div className="p-4 lg:p-6 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4 lg:mb-6">
            <div className="flex items-center">
              <div className="text-xl lg:text-2xl mr-2 lg:mr-3">🏛️</div>
              <h1 className="text-sm lg:text-base font-bold text-gray-800 whitespace-nowrap">FDA Export Assistant</h1>
            </div>
            {/* 모바일 닫기 버튼 */}
            <button
              onClick={() => setIsMobileMenuOpen(false)}
              className="lg:hidden p-1 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* 탭 네비게이션 */}
          <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('projects')}
              className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-md text-sm font-medium transition-all ${
                activeTab === 'projects'
                  ? 'bg-white text-indigo-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              프로젝트
            </button>
            <button
              onClick={() => setActiveTab('dictionary')}
              className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-md text-sm font-medium transition-all ${
                activeTab === 'dictionary'
                  ? 'bg-white text-indigo-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              용어사전
            </button>
          </div>
        </div>

        {/* 탭 컨텐츠 */}
        <div className="flex-1 overflow-y-auto">
          {activeTab === 'projects' ? (
            <div className="p-4 lg:p-6">
              <div className="mb-4 lg:mb-6">
                <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3 lg:mb-4">프로젝트</h2>
                <button
                  onClick={() => {
                    onCreateProject();
                    setIsMobileMenuOpen(false); // 모바일에서 프로젝트 생성 후 메뉴 닫기
                  }}
                  className="w-full bg-gradient-to-r from-indigo-500 to-indigo-600 text-white py-3 px-4 rounded-lg font-medium mb-4 hover:from-indigo-600 hover:to-indigo-700 transition-all duration-200 flex items-center justify-center"
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
                          onClick={() => {
                            onSelectProject(project.id);
                            setIsMobileMenuOpen(false); // 모바일에서 프로젝트 선택 후 메뉴 닫기
                          }}
                          className="flex-1 cursor-pointer"
                        >
                          {project.name}
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteProject(project.id);
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
            </div>
          ) : (
            <div className="p-4 lg:p-6">
              <TermDictionary />
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;


