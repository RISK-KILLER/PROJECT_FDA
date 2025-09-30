# rag.py
"""
PROJECT_FDA 문서 관리 CLI (ChromaDB 로컬 버전)
사용법:
  python rag.py embed --file ../../docs/development/coding-standards.md
  python rag.py search "프로젝트 구조는 어떻게 되어 있나요?"
  python rag.py update --all
  python rag.py sync    # GitHub docs 동기화
  python rag.py status  # 컬렉션 상태 확인
"""

import argparse
import sys
import subprocess
import shutil
from pathlib import Path
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, Document, Settings, StorageContext
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.node_parser import SemanticSplitterNodeParser
import chromadb

class ProjectRAGChroma:
    def __init__(self, collection_name=None, db_path="./chroma_db"):
        
        if collection_name is None:
            # 현재 Git 브랜치 이름 사용
            try:
                branch = subprocess.run(['git', 'branch', '--show-current'], 
                                    capture_output=True, text=True).stdout.strip()
                collection_name = f"project_docs_{branch.replace('/', '_')}"
            except:
                collection_name = "project_docs_main"

        self.collection_name = collection_name
        self.db_path = db_path
        self.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # ChromaDB 로컬 클라이언트 초기화
        self.chroma_client = chromadb.PersistentClient(path=self.db_path)
        self.chroma_collection = self.chroma_client.get_or_create_collection(self.collection_name)
        
        print(f"ChromaDB 로컬 저장소: {self.db_path}")
        print(f"컬렉션: {self.collection_name}")
        
    def get_collection_status(self):
        """컬렉션 상태 정보 조회"""
        try:
            count = self.chroma_collection.count()
            print(f"컬렉션 상태: {self.collection_name}")
            print(f"   - 벡터 개수: {count}")
            print(f"   - 저장 경로: {self.db_path}")
            print(f"   - 임베딩 모델: sentence-transformers/all-MiniLM-L6-v2")
            
        except Exception as e:
            print(f"상태 조회 실패: {e}")
    
    def embed_document(self, file_path):
        """단일 문서 임베딩 및 저장"""
        print(f"문서 임베딩 시작: {file_path}")
        
        try:
            # 문서 로드
            documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
            
            # 시멘틱 청킹
            splitter = SemanticSplitterNodeParser(
                buffer_size=1,
                breakpoint_percentile_threshold=60,
                embed_model=self.embed_model
            )
            
            # ChromaDB 벡터 스토어 설정
            vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # 인덱스 생성 및 저장
            index = VectorStoreIndex.from_documents(
                documents,
                transformations=[splitter],
                storage_context=storage_context,
                embed_model=self.embed_model
            )
            
            # 임베딩된 청크 수 확인
            nodes = splitter.get_nodes_from_documents(documents)
            print(f"임베딩 완료: {len(nodes)}개 청크 생성됨")
            
            return True
            
        except Exception as e:
            print(f"임베딩 실패: {e}")
            return False
        
    def search_documents(self, query, top_k=3):
        """문서 검색"""
        print(f"검색 쿼리: '{query}'")
        
        try:
            # ChromaDB 벡터 스토어 연결
            vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
            
            # 인덱스 로드
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=self.embed_model
            )
            
            # 검색 실행
            retriever = index.as_retriever(similarity_top_k=top_k*2)
            nodes = retriever.retrieve(query)
            
            # 검색어 키워드 기반 필터링
            filtered_nodes = []
            query_keywords = query.lower().split()
            
            for node in nodes:
                text_lower = node.text.lower()
                keyword_matches = sum(1 for keyword in query_keywords if keyword in text_lower)
                if keyword_matches > 0:
                    node.score += keyword_matches * 0.1
                    filtered_nodes.append(node)
            
            # 점수순 정렬 후 상위 결과 선택
            filtered_nodes.sort(key=lambda x: x.score, reverse=True)
            final_nodes = filtered_nodes[:top_k] if filtered_nodes else nodes[:top_k]
            
            if final_nodes:
                print("\n=== 검색 결과 ===")
                for i, node in enumerate(final_nodes, 1):
                    print(f"\n결과 {i} (유사도: {node.score:.3f})")
                    print("-" * 50)
                    text = node.text.strip()
                    if len(text) > 300:
                        print(text[:300] + "...")
                    else:
                        print(text)
                
                # Cursor AI용 컨텍스트
                print(f"\nCursor AI 컨텍스트:")
                print("=" * 60)
                cursor_context = "\n\n".join([node.text for node in final_nodes[:2]])
                print(cursor_context)
                print("=" * 60)
                
                return True
                
            else:
                print("검색 결과 없음")
                return False
                
        except Exception as e:
            print(f"검색 오류: {e}")
            return False
    
    def update_all_documents(self, data_dir="../../docs/"):
        """데이터 디렉토리의 모든 문서 업데이트"""
        print(f"전체 문서 업데이트 시작: {data_dir}")
        
        try:
            # 기존 컬렉션 삭제 후 재생성
            print("기존 컬렉션 삭제 중...")
            self.chroma_client.delete_collection(self.collection_name)
            self.chroma_collection = self.chroma_client.create_collection(self.collection_name)
            
        except Exception as e:
            print(f"컬렉션 삭제 중 오류: {e}")
            
        data_path = Path(data_dir)
        if not data_path.exists():
            print(f"데이터 디렉토리가 존재하지 않습니다: {data_dir}")
            return False
            
        # .md 파일 찾기
        md_files = list(data_path.rglob("*.md")) 
        if not md_files:
            print(".md 파일을 찾을 수 없습니다")
            return False
            
        # 모든 마크다운 파일 처리
        success_count = 0
        for file_path in md_files:
            print(f"처리 중: {file_path.name}")
            if self.embed_document(str(file_path)):
                success_count += 1
            
        print(f"전체 업데이트 완료: {success_count}/{len(md_files)}개 파일 처리")
        return success_count == len(md_files)
    
    def sync_github_docs(self, repo_url="https://github.com/RISK-KILLER/PROJECT_FDA", branch="dev"):
        """GitHub에서 docs 폴더 동기화"""
        print(f"GitHub에서 문서 동기화 중...")
        print(f"저장소: {repo_url}")
        print(f"브랜치: {branch}")
        
        try:
            docs_path = Path("../../docs")
            temp_path = Path("./temp_repo")
            
            # 기존 docs 폴더 백업
            if docs_path.exists():
                backup_path = Path("./docs_backup")
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                shutil.move(str(docs_path), str(backup_path))
                print("기존 docs 폴더 백업 완료")
            
            # 임시 폴더에 저장소 클론
            if temp_path.exists():
                shutil.rmtree(temp_path)
            
            result = subprocess.run([
                "git", "clone", "--depth", "1", "--branch", branch,
                repo_url, str(temp_path)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Git clone 실패: {result.stderr}")
                # 백업 복원
                if Path("./docs_backup").exists():
                    shutil.move("./docs_backup", str(docs_path))
                return False
            
            # docs 폴더만 복사
            repo_docs_path = temp_path / "docs"
            if repo_docs_path.exists():
                shutil.copytree(str(repo_docs_path), str(docs_path))
                print(f"docs 폴더 동기화 완료")
                
                # .md 파일 목록 출력
                md_files = list(docs_path.glob("*.md"))
                print(f"다운로드된 문서: {len(md_files)}개")
                for md_file in md_files:
                    print(f"  - {md_file.name}")
            else:
                print("저장소에 docs 폴더가 없습니다")
                return False
            
            # 임시 폴더 삭제
            shutil.rmtree(temp_path)
            
            # 백업 폴더 삭제
            if Path("./docs_backup").exists():
                shutil.rmtree(Path("./docs_backup"))
            
            return True
            
        except Exception as e:
            print(f"동기화 실패: {e}")
            # 오류 시 백업 복원
            if Path("./docs_backup").exists() and not docs_path.exists():
                shutil.move("./docs_backup", str(docs_path))
                print("백업에서 복원 완료")
            return False

    
    def delete_collection(self):
        """컬렉션 완전 삭제"""
        try:
            self.chroma_client.delete_collection(self.collection_name)
            print(f"컬렉션 '{self.collection_name}' 삭제 완료")
        except Exception as e:
            print(f"컬렉션 삭제 실패: {e}")

def main():
    parser = argparse.ArgumentParser(description="프로젝트 문서 관리 (ChromaDB 로컬)")
    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령어')
    
    # embed 명령어
    embed_parser = subparsers.add_parser('embed', help='문서 임베딩')
    embed_parser.add_argument('--file', required=True, help='임베딩할 파일 경로')
    
    # search 명령어
    search_parser = subparsers.add_parser('search', help='문서 검색')
    search_parser.add_argument('query', help='검색 쿼리')
    search_parser.add_argument('--top-k', type=int, default=3, help='검색 결과 수')
    
    # update 명령어
    update_parser = subparsers.add_parser('update', help='문서 업데이트')
    update_parser.add_argument('--all', action='store_true', help='모든 문서 업데이트')
    update_parser.add_argument('--dir', default='../../docs/', help='문서 디렉토리 경로')
    
    # sync 명령어 (새로 추가)
    sync_parser = subparsers.add_parser('sync', help='GitHub docs 동기화')
    sync_parser.add_argument('--repo', default='https://github.com/RISK-KILLER/PROJECT_FDA', help='저장소 URL')
    sync_parser.add_argument('--branch', default='dev', help='브랜치명')
    
    # status 명령어
    status_parser = subparsers.add_parser('status', help='컬렉션 상태 확인')
    
    # delete 명령어
    delete_parser = subparsers.add_parser('delete', help='컬렉션 삭제')
    delete_parser.add_argument('--confirm', action='store_true', help='삭제 확인')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    rag = ProjectRAGChroma()
    
    if args.command == 'embed':
        rag.embed_document(args.file)
        
    elif args.command == 'search':
        rag.search_documents(args.query, args.top_k)
        
    elif args.command == 'update':
        if args.all:
            rag.update_all_documents(args.dir)
        else:
            print("--all 플래그를 사용하세요")
    
    elif args.command == 'sync':
        if rag.sync_github_docs(args.repo, args.branch):
            print("동기화 완료. 문서를 업데이트하시겠습니까? (y/n)")
            if input().lower() == 'y':
                rag.update_all_documents()
        
    elif args.command == 'status':
        rag.get_collection_status()
        
    elif args.command == 'delete':
        if args.confirm:
            rag.delete_collection()
        else:
            print("정말 삭제하시려면 --confirm 플래그를 사용하세요")

if __name__ == "__main__":
    main()