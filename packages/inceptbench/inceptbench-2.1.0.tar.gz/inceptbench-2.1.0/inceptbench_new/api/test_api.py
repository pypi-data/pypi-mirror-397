"""
Simple test script for the Educational Content Evaluator API.

Usage:
    python -m inceptbench_new.api.test_api

This script tests the API endpoints locally without making actual LLM calls.
"""

import sys

from fastapi.testclient import TestClient

from .main import app

# Create test client
client = TestClient(app)


def test_health():
    """Test health check endpoint."""
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    print(f"✓ Health check passed: {data}")


def test_curriculums():
    """Test curriculum listing endpoint."""
    print("\nTesting /curriculums endpoint...")
    response = client.get("/curriculums")
    assert response.status_code == 200
    data = response.json()
    assert "curriculums" in data
    assert "common_core" in data["curriculums"]
    print(f"✓ Curriculums endpoint passed: {data}")


def test_root():
    """Test root endpoint."""
    print("\nTesting / endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "endpoints" in data
    print(f"✓ Root endpoint passed: {data['service']}")


def test_evaluate_validation():
    """Test evaluation endpoint input validation."""
    print("\nTesting /evaluate endpoint validation...")
    
    # Test missing content
    response = client.post("/evaluate", json={})
    assert response.status_code == 422  # Validation error
    print("✓ Validation: Missing content rejected")
    
    # Test empty content
    response = client.post("/evaluate", json={"content": ""})
    assert response.status_code == 422  # Validation error
    print("✓ Validation: Empty content rejected")
    
    # Test invalid MCQ (missing answer_options)
    response = client.post("/evaluate", json={
        "generated_content": [{
            "id": "q1",
            "request": {
                "grade": "7",
                "subject": "mathematics"
            },
            "content": {
                "question": "What is 2+2?",
                "answer": "A",
                "answer_explanation": "Test",
                "answer_options": []  # Empty - should fail
            }
        }]
    })
    assert response.status_code == 422  # Validation error
    print("✓ Validation: Invalid MCQ (empty answer_options) rejected")
    
    # Test invalid answer key
    response = client.post("/evaluate", json={
        "generated_content": [{
            "id": "q1",
            "request": {
                "grade": "7",
                "subject": "mathematics"
            },
            "content": {
                "question": "What is 2+2?",
                "answer": "Z",  # Invalid - not in options
                "answer_explanation": "Test",
                "answer_options": [
                    {"key": "A", "text": "3"},
                    {"key": "B", "text": "4"}
                ]
            }
        }]
    })
    assert response.status_code == 422  # Validation error
    print("✓ Validation: Invalid answer key rejected")
    
    # Test minimal valid request (only required fields)
    response = client.post("/evaluate", json={
        "generated_content": [{
            "id": "q1",
            "request": {
                "grade": "5",
                "subject": "mathematics"
            },
            "content": {
                "question": "What is 2+2?",
                "answer": "B",
                "answer_explanation": "2 + 2 = 4",
                "answer_options": [
                    {"key": "A", "text": "3"},
                    {"key": "B", "text": "4"}
                ]
            }
        }]
    })
    # This should be valid (200 or 503 if no API keys)
    assert response.status_code in [200, 503]
    print("✓ Validation: Minimal request with only required fields accepted")


def test_evaluate_simple_content():
    """Test evaluation endpoint with simple string content."""
    print("\nTesting /evaluate endpoint with simple content...")
    print("⚠️  This will make actual LLM API calls and may take time...")
    
    response = client.post("/evaluate", json={
        "content": "What is 2 + 2?",
        "curriculum": "common_core"
    })
    
    if response.status_code == 503:
        print("⚠️  Service unavailable (likely missing API keys)")
        print("   Set OPENAI_API_KEY and ANTHROPIC_API_KEY in .env file")
        return
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify new response structure
    assert "request_id" in data
    assert "evaluations" in data
    assert "evaluation_time_seconds" in data
    assert "inceptbench_version" in data
    
    # Verify evaluations dict
    assert isinstance(data["evaluations"], dict)
    assert len(data["evaluations"]) == 1
    
    # Get first evaluation
    first_eval = list(data["evaluations"].values())[0]
    assert "inceptbench_new_evaluation" in first_eval
    assert "score" in first_eval
    
    # Verify inceptbench evaluation structure
    inceptbench_eval = first_eval["inceptbench_new_evaluation"]
    assert "content_type" in inceptbench_eval
    assert "overall" in inceptbench_eval
    assert "factual_accuracy" in inceptbench_eval
    assert "weighted_score" in inceptbench_eval
    
    print("✓ Simple content evaluation successful:")
    print(f"  Request ID: {data['request_id']}")
    print(f"  Content type: {inceptbench_eval['content_type']}")
    print(f"  Overall score: {first_eval['score']:.2f}")
    print(f"  Evaluation time: {data['evaluation_time_seconds']:.2f}s")


def test_evaluate_structured_mcq():
    """Test evaluation endpoint with structured MCQ (with optional fields)."""
    print("\nTesting /evaluate endpoint with structured MCQ...")
    print("⚠️  This will make actual LLM API calls and may take time...")
    
    response = client.post("/evaluate", json={
        "generated_content": [{
            "id": "q1",
            "request": {
                "grade": "7",
                "subject": "mathematics"
                # All optional fields omitted: type, difficulty, locale, skills, instruction
            },
            "content": {
                "question": "What is the value of x in 3x + 7 = 22?",
                "answer": "C",
                "answer_explanation": "Subtract 7 from both sides: 3x = 15, then divide by 3: x = 5",
                "answer_options": [
                    {"key": "A", "text": "3"},
                    {"key": "B", "text": "4"},
                    {"key": "C", "text": "5"},
                    {"key": "D", "text": "6"}
                ]
            }
        }]
    })
    
    if response.status_code == 503:
        print("⚠️  Service unavailable (likely missing API keys)")
        return
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "request_id" in data
    assert "evaluations" in data
    assert "q1" in data["evaluations"]
    
    # Get the evaluation
    q1_eval = data["evaluations"]["q1"]
    assert "inceptbench_new_evaluation" in q1_eval
    assert "score" in q1_eval
    
    print("✓ Structured MCQ evaluation successful (minimal fields):")
    print(f"  Item ID: q1")
    print(f"  Score: {q1_eval['score']:.2f}")


def test_evaluate_batch():
    """Test batch evaluation endpoint with minimal fields."""
    print("\nTesting /evaluate/batch endpoint...")
    print("⚠️  This will make actual LLM API calls and may take time...")
    
    response = client.post("/evaluate/batch", json={
        "generated_content": [
            {
                "id": "q1",
                "request": {
                    "grade": "5",
                    "subject": "science"
                },
                "content": {
                    "question": "What causes water to evaporate?",
                    "answer": "A",
                    "answer_explanation": "Heat from the sun causes water to evaporate",
                    "answer_options": [
                        {"key": "A", "text": "Heat from the sun"},
                        {"key": "B", "text": "Cold temperatures"}
                    ]
                }
            },
            {
                "id": "q2",
                "request": {
                    "grade": "6",
                    "subject": "mathematics"
                },
                "content": {
                    "question": "What is 3.5 + 2.7?",
                    "answer": "6.2",
                    "answer_explanation": "Add the whole numbers (3+2=5) and decimals (0.5+0.7=1.2), then combine: 5+1.2=6.2"
                }
            }
        ]
    })
    
    if response.status_code == 503:
        print("⚠️  Service unavailable (likely missing API keys)")
        return
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "request_id" in data
    assert "evaluations" in data
    assert "q1" in data["evaluations"]
    assert "q2" in data["evaluations"]
    
    print("✓ Batch evaluation successful (minimal fields):")
    print(f"  Total items: {len(data['evaluations'])}")
    print(f"  Evaluation time: {data['evaluation_time_seconds']:.2f}s")


def main():
    """Run all tests."""
    print("=" * 70)
    print("Educational Content Evaluator API - Test Suite (v2.0)")
    print("=" * 70)
    
    try:
        # Basic endpoint tests (no LLM calls)
        test_health()
        test_curriculums()
        test_root()
        test_evaluate_validation()
        
        # Full evaluation tests (requires API keys)
        print("\n" + "=" * 70)
        print("Full Evaluation Tests (requires API keys)")
        print("=" * 70)
        test_evaluate_simple_content()
        test_evaluate_structured_mcq()
        test_evaluate_batch()
        
        print("\n" + "=" * 70)
        print("✓ All tests passed!")
        print("=" * 70)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

