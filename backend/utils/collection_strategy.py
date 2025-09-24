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
        'description': 'GRAS Notice inventory, approved substances, intended uses',
        'search_pattern': '[exact_ingredient_name] GRAS intended use [food_category]',
        'key_focus': ['GRN number', 'FDA no objection', 'use conditions']
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
    """
    업로드 시 임베딩 구조와 일치하도록 쿼리 생성
    """
    if collection == 'dwpe':
        # 업로드: "Import Alert {id}: {title} - {reason} Products: {products}"
        # 검색도 동일한 구조로
        products = ' '.join(decomposition.get('ingredients', []))
        origin = decomposition.get('origin', '')
        category = decomposition.get('category', 'food')
        return f"Import Alert: {category} from {origin} - food safety Products: {products}"
    
    elif collection == 'ecfr':
        # 업로드: "{regulation_section}: {title} - {content}"
        processes = ' '.join(decomposition.get('processes', [])[:2])
        category = decomposition.get('category', 'food')
        return f"21 CFR: {category} processing - {processes} manufacturing requirements"
    
    elif collection == 'fsvp':
        # 업로드: "FSVP: {question} {original_text} Summary: {summary}"
        origin = decomposition.get('origin', 'foreign')
        category = decomposition.get('category', 'food')
        return f"FSVP: What are requirements for {category} from {origin} Summary: foreign supplier verification"
    
    elif collection == 'gras':
        # 업로드: "GRAS {grn}: {substance} - {intended_use} Status: {status} Content: {text}"
        ingredients = decomposition.get('ingredients', [])
        if ingredients:
            substances = ' '.join(ingredients[:3])
            return f"GRAS: {substances} - food ingredient use Status: no objection Content: safe for consumption"
        return "GRAS: food ingredients - general use Status: approved"
    
    elif collection == 'guidance':
        # 업로드: "Guidance {title}: {text} Category: {category}"
        category = decomposition.get('category', 'food')
        allergens = decomposition.get('allergens', [])
        if allergens:
            allergen_text = ' '.join(allergens)
            return f"Guidance allergen labeling: {allergen_text} requirements Category: {category}"
        return f"Guidance food labeling: {category} requirements Category: {category}"
    
    elif collection == 'rpm':
        # 업로드: "RPM Chapter {chapter} Section {section_id}: {section_title} {original_text}"
        import_type = decomposition.get('import_type', 'commercial')
        return f"RPM Chapter 9 Section: import procedures {import_type} shipments"
    
    elif collection == 'usc':
        # 업로드: "{regulation_section}: {title} - {content}"
        category = decomposition.get('category', 'food')
        return f"21 U.S.C.: {category} labeling - misbranding adulteration requirements"
    
    return f"FDA requirements for {decomposition.get('category', 'food')}"

def smart_collection_selection(decomposition: dict) -> list:
    """
    제품 특성에 따른 지능형 컬렉션 선택 (최대 7개)
    """
    selected = set()

    # 1단계: 필수 컬렉션 (3개)
    essential = ['guidance', 'ecfr', 'fsvp']
    selected.update(essential)

    # 2단계: 위험도 기반 선택
    if decomposition.get('risk_level') == 'high':
        selected.add('ecfr')  # 제조 공정 중요 (이미 essential에 있음)
        selected.add('usc')   # 법적 기반

    # 3단계: 알레르겐 유무
    if decomposition.get('allergens'):
        selected.add('guidance')  # 이미 essential에 있음

    # 4단계: 보관 방식
    if decomposition.get('storage_type') in ['frozen', 'refrigerated']:
        selected.add('ecfr')  # 온도 관리 규정 (이미 essential에 있음)

    # 5단계: 재료 복잡도
    if len(decomposition.get('ingredients', [])) > 3:
        selected.add('gras')  # 많은 재료 = 첨가물 확인

    # 6단계: 특정 위험 요소
    potential_hazards = decomposition.get('potential_hazards', [])
    if any(hazard in str(potential_hazards) for hazard in ['histamine', 'botulism', 'pathogen']):
        selected.add('ecfr')  # 제조 규정 (이미 essential에 있음)

    # 7단계: 수입 유형
    if decomposition.get('import_type') == 'personal use':
        selected.add('rpm')  # 개인용 수입 절차

    # 8단계: 원산지가 있으면 Import Alert 확인
    if decomposition.get('origin'):
        selected.add('dwpe')

    # 9단계: 법적 기반은 항상 포함
    selected.add('usc')

    return list(selected)[:7]  # 최대 7개로 제한

def prioritize_results_enhanced(search_results: dict, decomposition: dict) -> dict:
    """
    카테고리별 분류만 제공 (점수 조작 없음)
    """
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
