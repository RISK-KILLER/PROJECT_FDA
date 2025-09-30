# utils/tools.py
from llama_index.core.tools import QueryEngineTool
from llama_index.core import VectorStoreIndex
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def create_fda_tools():
    """FDA 컬렉션별 QueryEngineTool 생성 (강화된 description)"""
    
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    
    embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        dimensions=1536
    )
    
    llm = OpenAI(model="gpt-4o-mini", temperature=0)
    
    # 실제 존재하는 컬렉션 목록
    actual_collections = ['dwpe', 'ecfr', 'fsvp', 'gras', 'guidance', 'rpm', 'usc']
    
    tools = []
    
    for collection_name in actual_collections:
        try:
            vector_store = QdrantVectorStore(
                client=client,
                collection_name=collection_name
            )
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            index = VectorStoreIndex.from_vector_store(
                vector_store,
                storage_context=storage_context,
                embed_model=embed_model
            )
            query_engine = index.as_query_engine(
                llm=llm,
                similarity_top_k=5
            )
            
            # 컬렉션별 강화된 description
            if collection_name == "gras":
                description = """Search GRAS (Generally Recognized As Safe) database.
                
**Use this tool for:**
- Keywords: "GRN", "GRAS", "물질", "첨가물", "substance", "approved", "withdrawn"
- Food ingredient safety, additive approval status
                
**Query must be in ENGLISH. Translate Korean:**
- "대두" → "soy soybean"
- "음료" → "beverage drink"
- "승인된" → "approved no objection"
                """
                
            elif collection_name == "ecfr":
                description = """Search 21 CFR (Code of Federal Regulations).
                
**Use this tool for:**
- Keywords: "CFR", "21 CFR", "규정", "제조", "HACCP", "regulation"
- Manufacturing standards, CGMP, food safety regulations
                
**Query must be in ENGLISH:**
- "냉동식품" → "frozen food"
- "HACCP" → "HACCP hazard analysis critical control"
                
**For CFR numbers, add topic:** "21 CFR 73.1" → "21 CFR 73.1 color additive diluents"
                """
                
            elif collection_name == "dwpe":
                description = """Search Import Alert and detention database (DWPE).
                
**Use this tool for:**
- Keywords: "Import Alert", "Red List", "수입 거부", "detention"
- Country-specific violations, automatic detention
                
**Query must be in ENGLISH with synonyms:**
- "해산물" → "fish fishery seafood shellfish aquatic marine"
- "중국" → "China Chinese"
- "수입 거부" → "import alert detention refusal"
                """
                
            elif collection_name == "rpm":
                description = """Search Regulatory Procedures Manual (RPM).
                
**Use this tool for:**
- Keywords: "Chapter", "Section", "RPM", "절차", "procedure", "personal", "relabeling"
- Import procedures, detention processes, personal importation
                
**CRITICAL: Query must be in ENGLISH:**
- "개인용 수입" → "personal importation personal use"
- "절차" → "procedures process"
- "검사 거부" → "refusal entry detention"
- "relabeling 비용" → "relabeling supervision costs"
                
**For Section IDs:** "Chapter 9 Section 9-1-6" → "Chapter 9 Section 9-1-6 relabeling supervision"
                """
                
            elif collection_name == "usc":
                description = """Search 21 USC (United States Code) legal provisions.
                
**Use this tool for:**
- Keywords: "21 USC", "U.S.C", "법률", "처벌", "penalties", "misbranding"
- Legal definitions, prohibited acts, penalties
                
**DO NOT use for RPM Chapters/Sections!**
                
**Query must be in ENGLISH:**
- "부정표시" → "misbranding false labeling"
- "처벌" → "penalties violations sanctions"
                """
                
            elif collection_name == "fsvp":
                description = """Search Foreign Supplier Verification Program (FSVP) guidance.
                
**Use this tool for:**
- Keywords: "FSVP", "수입자", "검증", "supplier verification", "importer"
- Importer responsibilities, foreign supplier verification, FSVP compliance
                
**Query must be in ENGLISH:**
- "수입자 의무" → "importer responsibilities verification requirements"
- "검증 절차" → "verification procedures audit requirements"
                
**Covers:** 21 CFR 1.500-1.514, exemptions, recordkeeping
                """
                
            elif collection_name == "guidance":
                description = """Search FDA Guidance Documents and CPG.
                
**Use this tool for:**
- Keywords: "Guidance", "CPG", "가이드", "라벨링", "labeling", "allergen"
- Policy interpretations, compliance recommendations, labeling requirements
                
**Query must be in ENGLISH:**
- "라벨링 요구사항" → "labeling requirements"
- "알레르기 표시" → "allergen declaration labeling"
                
**Can search by:** CPG document number (e.g., 'CPG 500.200')
                """
            
            else:
                description = f"Search {collection_name} collection"
            
            tool = QueryEngineTool.from_defaults(
                query_engine=query_engine,
                name=collection_name,
                description=description
            )
            tools.append(tool)
            
        except Exception as e:
            print(f"Warning: Could not create tool for {collection_name}: {e}")
            continue
    
    return tools