# utils/collection_strategy.py
"""
실제 Qdrant 컬렉션에 맞춘 검색 전략 정의
"""

COLLECTION_STRATEGY = {
    'dwpe': {
        'role': '🚫 Import Alert Database (수입 거부 이력)',
        'description': 'FDA Import Alerts, detention without physical examination, red list companies',
        'search_pattern': '[origin] [product_type] Import Alert detention red list',
        'key_focus': ['country violations', 'company red list', 'automatic detention']
    },
    
    'ecfr': {
        'role': '📏 Electronic Code of Federal Regulations (연방 규정)',
        'description': '21 CFR regulations - specific requirements, tolerances, specifications',
        'search_pattern': '21 CFR [part_number] [substance] [process] requirements',
        'key_focus': ['numerical limits', 'specifications', 'CGMP', 'HACCP']
    },
    
    'fsvp': {
        'role': '📋 Foreign Supplier Verification Program (수입자 검증)',
        'description': 'Importer responsibilities, supplier verification, hazard analysis',
        'search_pattern': 'foreign supplier [risk_level] verification [product_category]',
        'key_focus': ['verification frequency', 'audit requirements', 'hazard control']
    },
    
    'gras': {
        'role': '✅ Generally Recognized As Safe Database',
        'description': '''GRAS Notice inventory with approval status filtering.
                
        Search Strategy:
        - For approved substances: Use keywords like "approved", "no objection", "승인된"
        - For recent filings: Mention year (e.g., "2023", "2024", "최근")
        - For specific substances: Use ingredient name in English or Korean
        - For withdrawn items: Use keywords like "withdrawn", "철회"

        The tool can search by:
        1. Substance name (물질명)
        2. Intended use (용도)
        3. Notifier company (신청 회사)
        4. Status (상태: approved/withdrawn)
        5. Filing year (제출 연도)

        Examples:
        - "음료용 승인된 GRAS" → finds approved substances for beverages
        - "2023년 제출 GRAS" → finds filings from 2023
        - "대두 관련 GRAS" → finds soy-related substances
        ''',
        'search_pattern': '[substance] GRAS [intended_use] [status] [year]',
        'key_focus': ['GRN number', 'approval status', 'intended use', 'filing year']
    },
    
    'guidance': {
        'role': '📖 FDA Guidance Documents (정책 가이드)',
        'description': 'CPG, labeling guides, allergen guidance, additives policy',
        'search_pattern': '[category] [topic] compliance policy guidance',
        'key_focus': ['labeling requirements', 'allergen controls', 'enforcement policy']
    },
    
    'rpm': {
        'role': '🔧 Regulatory Procedures Manual (운영 절차)',
        'description': 'Import procedures, detention, personal use, mail shipments',
        'search_pattern': '[import_type] shipment detention personal use procedures',
        'key_focus': ['3-month supply', 'personal importation', 'detention procedures']
    },
    
    'usc': {
        'role': '⚖️ United States Code (연방 법률)',
        'description': '21 USC - legal definitions, prohibitions, requirements',
        'search_pattern': '21 USC 343 [topic] misbranding adulteration',
        'key_focus': ['legal definitions', 'prohibited acts', 'penalties']
    }
}

def generate_optimized_query(collection: str, decomposition: dict) -> str:
    """컬렉션별 최적화된 쿼리 생성"""
    
    if collection == 'dwpe':
        products = ' '.join(decomposition.get('ingredients', []))
        origin = decomposition.get('origin', '')
        category = decomposition.get('category', 'food')
        return f"Import Alert: {category} from {origin} - food safety Products: {products}"
    
    elif collection == 'ecfr':
        processes = ' '.join(decomposition.get('processes', [])[:2])
        category = decomposition.get('category', 'food')
        return f"21 CFR: {category} processing - {processes} manufacturing requirements"
    
    elif collection == 'fsvp':
        origin = decomposition.get('origin', 'foreign')
        category = decomposition.get('category', 'food')
        return f"FSVP: What are requirements for {category} from {origin} Summary: foreign supplier verification"
    
    elif collection == 'gras':
        ingredients = decomposition.get('ingredients', [])
        if ingredients:
            substances = ' '.join(ingredients[:3])
            return f"GRAS: {substances} - food ingredient use Status: no objection Content: safe for consumption"
        return "GRAS: food ingredients - general use Status: approved"
    
    elif collection == 'guidance':
        category = decomposition.get('category', 'food')
        allergens = decomposition.get('allergens', [])
        if allergens:
            allergen_text = ' '.join(allergens)
            return f"Guidance allergen labeling: {allergen_text} requirements Category: {category}"
        return f"Guidance food labeling: {category} requirements Category: {category}"
    
    elif collection == 'rpm':
        import_type = decomposition.get('import_type', 'commercial')
        return f"RPM Chapter 9 Section: import procedures {import_type} shipments"
    
    elif collection == 'usc':
        category = decomposition.get('category', 'food')
        return f"21 U.S.C.: {category} labeling - misbranding adulteration requirements"
    
    return f"FDA requirements for {decomposition.get('category', 'food')}"


def smart_collection_selection(decomposition: dict) -> list:
    """
    모든 컬렉션을 검색하여 정보 누락 방지
    조건문 없이 항상 7개 전체 반환
    """
    return ['ecfr', 'fsvp', 'guidance', 'gras', 'dwpe', 'rpm', 'usc']


def prioritize_results_enhanced(search_results: dict, decomposition: dict) -> dict:
    """카테고리별 분류 (가중치 없음)"""
    
    categorized = {
        'regulations': [],      # 규정 (ecfr, usc)
        'guidance': [],         # 가이드 (guidance, rpm)
        'safety': [],          # 안전성 (gras, dwpe)
        'verification': [],    # 검증 (fsvp)
    }
    
    for collection, results in search_results.items():
        if collection in ['ecfr', 'usc']:
            categorized['regulations'].extend(results)
        elif collection in ['guidance', 'rpm']:
            categorized['guidance'].extend(results)
        elif collection in ['gras', 'dwpe']:
            categorized['safety'].extend(results)
        elif collection == 'fsvp':
            categorized['verification'].extend(results)
    
    # 각 카테고리 내에서 점수순 정렬 (가중치 없음)
    for category in categorized:
        categorized[category].sort(key=lambda x: x.get('score', 0), reverse=True)
    
    return categorized