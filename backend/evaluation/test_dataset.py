# evaluation/test_dataset.py
"""
FDA RAG 시스템 평가용 데이터셋
"""

from typing import List, Dict, Any

# 테스트 케이스 정의
FDA_TEST_DATASET = [
    {
        "id": "authority_001",
        "category": "authority",
        "difficulty": "critical",
        "question": "Can FDA add other allergens to the current list?",
        "ground_truth": "No. The list of major food allergens is determined by Congress under Section 201(qq) of the FD&C Act. FDA cannot alter this statutory list.",
        "expected_keywords": ["Congress", "cannot", "statutory", "Section 201(qq)", "determined by"],
        "expected_collections": ["guidance", "usc"],
        "expected_answer_type": "no",
        "context_required": ["legal authority", "statutory definition"],
        "notes": "Critical test - must not confuse major vs nonmajor allergens"
    },
    
    {
        "id": "authority_002",
        "category": "authority",
        "difficulty": "medium",
        "question": "Who determines the major food allergen list?",
        "ground_truth": "Congress determines the list under Section 201(qq) of the FD&C Act.",
        "expected_keywords": ["Congress", "Section 201", "FD&C Act"],
        "expected_collections": ["usc", "guidance"],
        "expected_answer_type": "congress",
        "context_required": ["legal authority"],
        "notes": "Should clearly state Congress, not FDA"
    },
    
    {
        "id": "definition_001",
        "category": "definition",
        "difficulty": "easy",
        "question": "What is a major food allergen?",
        "ground_truth": "A major food allergen includes milk, eggs, fish, crustacean shellfish, tree nuts, peanuts, wheat, soybeans, and sesame under Section 201(qq).",
        "expected_keywords": ["milk", "eggs", "fish", "shellfish", "nuts", "peanuts", "wheat", "soy", "sesame", "nine"],
        "expected_collections": ["guidance", "usc", "ecfr"],
        "expected_answer_type": "list",
        "context_required": ["allergen list"],
        "notes": "Should list all 9 major allergens"
    },
    
    {
        "id": "labeling_001",
        "category": "labeling",
        "difficulty": "medium",
        "question": "Do allergen labeling requirements provide specific direction for declaring major food allergens?",
        "ground_truth": "Yes. Major food allergens must be declared either in the ingredient list or in a Contains statement immediately after the ingredient list.",
        "expected_keywords": ["ingredient list", "Contains statement", "declare", "labeling"],
        "expected_collections": ["guidance", "ecfr"],
        "expected_answer_type": "yes",
        "context_required": ["labeling requirements"],
        "notes": "Two methods: ingredient list or Contains statement"
    },
    
    {
        "id": "import_001",
        "category": "import",
        "difficulty": "medium",
        "question": "중국산 새우 Import Alert?",
        "ground_truth": "Check DWPE for Import Alerts related to Chinese seafood products.",
        "expected_keywords": ["Import Alert", "China", "seafood", "shrimp", "detention"],
        "expected_collections": ["dwpe", "ecfr"],
        "expected_answer_type": "reference",
        "context_required": ["import alerts", "detention"],
        "notes": "Korean query - should search in English"
    },
    
    {
        "id": "procedure_001",
        "category": "procedure",
        "difficulty": "hard",
        "question": "What are FSVP requirements for food importers?",
        "ground_truth": "Foreign Supplier Verification Program (FSVP) requires importers to verify their foreign suppliers and ensure imported food meets US safety standards.",
        "expected_keywords": ["FSVP", "foreign supplier", "verification", "importer", "requirements"],
        "expected_collections": ["fsvp", "ecfr"],
        "expected_answer_type": "explanation",
        "context_required": ["importer obligations", "verification procedures"],
        "notes": "Should explain FSVP basics"
    },
    
    {
        "id": "product_001",
        "category": "product",
        "difficulty": "hard",
        "question": "김치 미국 수출 규정?",
        "ground_truth": "Kimchi export requires compliance with FDA registration, HACCP/HARPC, allergen labeling, and import requirements.",
        "expected_keywords": ["kimchi", "registration", "HACCP", "labeling", "import"],
        "expected_collections": ["guidance", "ecfr", "fsvp"],
        "expected_answer_type": "comprehensive",
        "context_required": ["product decomposition", "multiple regulations"],
        "notes": "Korean product - should decompose and search comprehensively"
    },
]


def get_dataset() -> List[Dict[str, Any]]:
    """평가 데이터셋 반환"""
    return FDA_TEST_DATASET


def get_dataset_by_category(category: str) -> List[Dict[str, Any]]:
    """카테고리별 데이터셋 반환"""
    return [item for item in FDA_TEST_DATASET if item['category'] == category]


def get_dataset_by_difficulty(difficulty: str) -> List[Dict[str, Any]]:
    """난이도별 데이터셋 반환"""
    return [item for item in FDA_TEST_DATASET if item['difficulty'] == difficulty]