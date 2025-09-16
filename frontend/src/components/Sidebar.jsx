import React from 'react';
import { Plus, X } from 'lucide-react';

const Sidebar = ({ projects, onCreateProject, onSelectProject, onDeleteProject }) => {
  return (
    <div className="w-80 bg-white/95 backdrop-blur-sm border-r border-gray-200 p-6 flex flex-col">
      <div className="flex items-center mb-8">
        <div className="text-2xl mr-3">🏛️</div>
        <h1 className="text-xl font-bold text-gray-800">FDA Export Assistant</h1>
      </div>

      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">프로젝트</h2>
        <button
          onClick={onCreateProject}
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
                  onClick={() => onSelectProject(project.id)}
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
  );
};

export default Sidebar;


