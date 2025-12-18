# API Usage Examples

This document provides real-world examples of using the Educational Content Evaluator API.

## Table of Contents
- [Basic Question](#basic-question)
- [Math Problem](#math-problem)
- [Multiple Choice Quiz](#multiple-choice-quiz)
- [Reading Passage](#reading-passage)
- [Content with Images](#content-with-images)
- [Error Handling](#error-handling)

---

## Basic Question

### Request
```json
POST /evaluate
{
  "content": "What is the capital of France?",
  "curriculum": "common_core"
}
```

### Response (abbreviated)
```json
{
  "content_type": "question",
  "overall": {
    "score": 0.62,
    "reasoning": "This is a simple factual recall question...",
    "suggested_improvements": "Consider adding a misconception-revealing distractor..."
  },
  "factual_accuracy": {
    "score": 1.0,
    "reasoning": "Paris is indeed the capital of France...",
    "suggested_improvements": null
  },
  "educational_accuracy": {
    "score": 1.0,
    "reasoning": "The question serves its educational purpose...",
    "suggested_improvements": null
  },
  "curriculum_alignment": {
    "score": 1.0,
    "reasoning": "Aligns with geography and world knowledge standards...",
    "suggested_improvements": null
  }
}
```

---

## Math Problem

### Request
```json
POST /evaluate
{
  "content": "Solve for x: 2x + 5 = 15\nA) x = 5\nB) x = 10\nC) x = 7.5\nD) x = 2.5",
  "curriculum": "common_core"
}
```

### Response (abbreviated)
```json
{
  "content_type": "question",
  "overall": {
    "score": 0.92,
    "reasoning": "Well-constructed algebra problem with appropriate difficulty...",
    "suggested_improvements": null
  },
  "factual_accuracy": {
    "score": 1.0,
    "reasoning": "Correct answer is A) x = 5...",
    "suggested_improvements": null
  },
  "distractor_quality": {
    "score": 1.0,
    "reasoning": "Distractors represent common student errors...",
    "suggested_improvements": null
  },
  "curriculum_alignment": {
    "score": 1.0,
    "reasoning": "Aligns with Common Core standard 6.EE.B.7...",
    "suggested_improvements": null
  }
}
```

---

## Multiple Choice Quiz

### Request
```json
POST /evaluate
{
  "content": "Science Quiz\n\n1. What is photosynthesis?\nA) The process plants use to make food\nB) The process of breathing\nC) The process of cell division\nD) The process of digestion\n\n2. Which organelle performs photosynthesis?\nA) Nucleus\nB) Mitochondria\nC) Chloroplast\nD) Ribosome\n\n3. What gas do plants take in during photosynthesis?\nA) Oxygen\nB) Nitrogen\nC) Carbon dioxide\nD) Hydrogen",
  "curriculum": "common_core"
}
```

### Response (abbreviated)
```json
{
  "content_type": "quiz",
  "overall": {
    "score": 0.88,
    "reasoning": "Well-organized quiz on photosynthesis...",
    "suggested_improvements": "Consider varying question formats..."
  },
  "concept_coverage": {
    "score": 1.0,
    "reasoning": "Covers key concepts comprehensively...",
    "suggested_improvements": null
  },
  "answer_balance": {
    "score": 1.0,
    "reasoning": "Statistical analysis shows balanced distribution...",
    "suggested_improvements": null
  },
  "difficulty_distribution": {
    "score": 1.0,
    "reasoning": "Good progression from basic to advanced...",
    "suggested_improvements": null
  }
}
```

---

## Reading Passage

### Request
```json
POST /evaluate
{
  "content": "The Story of the Tortoise and the Hare\n\nOnce upon a time, a speedy hare made fun of a slow tortoise. The tortoise, tired of being laughed at, challenged the hare to a race. The hare, confident in his speed, quickly accepted.\n\nWhen the race began, the hare sprinted ahead, leaving the tortoise far behind. Feeling confident, the hare decided to take a nap under a tree. Meanwhile, the tortoise kept moving slowly but steadily.\n\nWhen the hare woke up, he saw the tortoise crossing the finish line. The moral of the story: Slow and steady wins the race.\n\nComprehension Questions:\n1. Why did the tortoise challenge the hare?\n2. What did the hare do during the race?\n3. What is the moral of this story?",
  "curriculum": "common_core"
}
```

### Response (abbreviated)
```json
{
  "content_type": "fiction_reading",
  "overall": {
    "score": 0.87,
    "reasoning": "Classic fable with clear moral lesson...",
    "suggested_improvements": "Consider adding more descriptive language..."
  },
  "reading_level_match": {
    "score": 1.0,
    "reasoning": "Appropriate vocabulary and sentence structure...",
    "suggested_improvements": null
  },
  "engagement": {
    "score": 1.0,
    "reasoning": "Classic story with clear conflict and resolution...",
    "suggested_improvements": null
  },
  "question_quality": {
    "score": 1.0,
    "reasoning": "Questions test comprehension at multiple levels...",
    "suggested_improvements": null
  }
}
```

---

## Content with Images

### Request
```json
POST /evaluate
{
  "content": "Look at the image below showing baskets of apples:\nhttps://example.com/images/apple-baskets.jpg\n\nQuestion: If each basket contains 4 apples and there are 3 baskets, how many apples are there in total?\nA) 7\nB) 12\nC) 16\nD) 9",
  "curriculum": "common_core"
}
```

### Response (abbreviated with object counting)
```json
{
  "content_type": "question",
  "overall": {
    "score": 0.95,
    "reasoning": "Excellent visual math problem with real-world context...",
    "suggested_improvements": null
  },
  "stimulus_quality": {
    "score": 1.0,
    "reasoning": "Image shows clear, countable objects. Object count analysis confirms 3 baskets with 4 apples each...",
    "suggested_improvements": null
  },
  "factual_accuracy": {
    "score": 1.0,
    "reasoning": "Correct answer is B) 12. Object counting confirms 12 total apples...",
    "suggested_improvements": null
  }
}
```

**Note:** The API automatically:
1. Detects image URLs in content
2. Downloads and encodes images
3. Performs object counting (bias-free, multi-method verification)
4. Includes count data in evaluation

---

## Error Handling

### Invalid Curriculum

**Request:**
```json
POST /evaluate
{
  "content": "What is 2+2?",
  "curriculum": "invalid_curriculum"
}
```

**Response:**
```json
HTTP 400 Bad Request
{
  "detail": "Curriculum 'invalid_curriculum' not supported. Available: ['common_core']"
}
```

### Missing Content

**Request:**
```json
POST /evaluate
{
  "curriculum": "common_core"
}
```

**Response:**
```json
HTTP 422 Unprocessable Entity
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "content"],
      "msg": "Field required"
    }
  ]
}
```

### Empty Content

**Request:**
```json
POST /evaluate
{
  "content": "",
  "curriculum": "common_core"
}
```

**Response:**
```json
HTTP 422 Unprocessable Entity
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "content"],
      "msg": "String should have at least 1 character"
    }
  ]
}
```

### Service Unavailable

**Scenario:** API keys not configured

**Response:**
```json
HTTP 503 Service Unavailable
{
  "detail": "Service initialization failed: OPENAI_API_KEY environment variable is required"
}
```

### Internal Server Error

**Scenario:** Unexpected error during evaluation

**Response:**
```json
HTTP 500 Internal Server Error
{
  "error": "InternalServerError",
  "message": "An unexpected error occurred",
  "detail": null
}
```

**Note:** `detail` is only included when `LOG_LEVEL=DEBUG`

---

## Advanced Usage

### Custom Headers

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: my-request-123" \
  -d '{"content": "..."}'
```

**Response includes:**
```
HTTP/1.1 200 OK
X-Process-Time: 12.456
Content-Type: application/json
```

### Timeout Handling

For long evaluations, ensure your HTTP client timeout is set appropriately:

```python
import requests

response = requests.post(
    "http://localhost:8000/evaluate",
    json={"content": "...very long content..."},
    timeout=300  # 5 minutes
)
```

### Batch Processing

```python
import asyncio
import aiohttp

async def evaluate_batch(contents):
    async with aiohttp.ClientSession() as session:
        tasks = [
            session.post(
                "http://localhost:8000/evaluate",
                json={"content": content}
            )
            for content in contents
        ]
        responses = await asyncio.gather(*tasks)
        return [await r.json() for r in responses]

# Use
contents = ["Content 1", "Content 2", "Content 3"]
results = asyncio.run(evaluate_batch(contents))
```

---

## Response Schema

All evaluations return this base structure:

```json
{
  "content_type": "question|quiz|fiction_reading|nonfiction_reading|other",
  "overall": {
    "score": 0.0-1.0,
    "reasoning": "string",
    "suggested_improvements": "string|null"
  },
  "factual_accuracy": {
    "score": 0.0|1.0,
    "reasoning": "string",
    "suggested_improvements": "string|null"
  },
  "educational_accuracy": {
    "score": 0.0|1.0,
    "reasoning": "string",
    "suggested_improvements": "string|null"
  },
  // ... content-type-specific metrics ...
}
```

### Metric Score Interpretation

- **Overall:** Continuous score 0.0-1.0
  - `0.85-0.99`: Acceptable quality
  - `0.99-1.0`: Superior quality
  - `< 0.85`: Needs improvement

- **All other metrics:** Binary 0.0 or 1.0
  - `1.0`: Passes the criterion
  - `0.0`: Fails the criterion

### Content-Specific Metrics

**Question:**
- `curriculum_alignment`
- `clarity_precision`
- `reveals_misconceptions`
- `difficulty_alignment`
- `passage_reference`
- `distractor_quality`
- `stimulus_quality`
- `mastery_learning_alignment`

**Quiz:**
- `concept_coverage`
- `difficulty_distribution`
- `non_repetitiveness`
- `test_preparedness`
- `answer_balance` (computed programmatically)

**Reading Passage (Fiction/Nonfiction):**
- `reading_level_match`
- `length_appropriateness`
- `topic_focus`
- `engagement`
- `accuracy_and_logic`
- `question_quality`

**Other:**
- `educational_value`
- `direct_instruction_alignment`
- `content_appropriateness`
- `clarity_and_organization`
- `engagement`

---

## Interactive Documentation

For even more examples and to test the API interactively:

1. Start the API: `uvicorn src.api.main:app --reload`
2. Visit: http://localhost:8000/docs
3. Click "Try it out" on any endpoint
4. Enter your request and click "Execute"
5. See the response immediately

The interactive docs include:
- Request/response schemas
- Example values
- Validation rules
- Error responses
- Try-it-out functionality

