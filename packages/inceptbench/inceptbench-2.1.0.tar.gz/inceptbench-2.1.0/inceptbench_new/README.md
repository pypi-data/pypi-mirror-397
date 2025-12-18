# Educational Content Evaluator

A production-ready system for evaluating educational content quality using LLM-based analysis.

## Overview

This system evaluates educational content across multiple quality dimensions, providing:
- **Automated Classification**: Determines content type (question, quiz, reading passage, etc.)
- **Comprehensive Evaluation**: Assesses content across 8-11 metrics depending on type
- **Standardized Output**: Consistent JSON schema with scores, reasoning, and improvement suggestions
- **Curriculum-Aware**: Integrates curriculum standards via vector store search
- **Image Analysis**: Counts objects in images and analyzes stimulus quality

## Architecture

```
Content String → Classifier → Router → Evaluator → JSON Response
                                  ↓
                            [Tools: curriculum, object counting]
```

### Components

- **models/**: Pydantic data models for requests, responses, and metrics
- **classifier/**: LLM-based content type classification
- **evaluators/**: Content-type-specific evaluators (question, quiz, reading, other)
- **router/**: Routes content to appropriate evaluator
- **service.py**: Main orchestration service
- **tools/**: Utility tools (curriculum search, image analysis)
- **config/**: Configuration and settings
- **prompts/**: External prompt files for easy maintenance

## Installation

### Prerequisites

- Python 3.11+
- OpenAI API key (required)
- Anthropic API key (for object counting)

### Setup

1. **Install dependencies**:

```bash
# From the project root
pip install -r src/requirements.txt

# Or install manually
pip install pydantic python-dotenv openai anthropic google-genai requests scipy
```

2. **Create `.env` file** in the project root (`/Users/shawnsullivan/gt-code/inceptbench/.env`):

```bash
# .env file (create this in the project root, NOT in src/)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here  # Optional
LOG_LEVEL=INFO  # Optional
```

The system will automatically load API keys from the `.env` file. Make sure to add `.env` to your `.gitignore` to avoid committing secrets!

**Note**: Vector store IDs are hardcoded in `src/config/settings.py` and are not user-configurable. Users specify curriculum by name (e.g., "common_core"), not by vector store ID.

## Usage

### CLI

Basic usage:

```bash
# Evaluate a string
python -m src.cli "What is 2+2? A) 3 B) 4 C) 5 D) 6"

# Evaluate from file
python -m src.cli --file question.txt

# Use different curriculum
python -m src.cli --curriculum common_core --file content.txt

# Save results to file
python -m src.cli --file content.txt --output results.json

# Consider generation prompt when evaluating
python -m src.cli --file content.txt --generation-prompt "The prompt"
python -m src.cli --file content.txt --generation-prompt-file prompt.txt

# Verbose mode
python -m src.cli --file content.txt --verbose
```

### Programmatic Usage

```python
import asyncio
from src.service import EvaluationService

async def evaluate_content():
    service = EvaluationService()
    
    # Evaluate content
    result = await service.evaluate(
        content="Your educational content here",
        curriculum="common_core"
    )
    
    # Access results
    print(f"Overall Score: {result.overall.score}")
    print(f"Content Type: {result.content_type}")
    
    # Get as JSON
    json_result = await service.evaluate_json(
        content="Your content",
        curriculum="common_core"
    )
    print(json_result)

asyncio.run(evaluate_content())
```

## Content Types

The system supports 5 content types:

1. **question**: Single questions (multiple choice, short answer, etc.)
2. **quiz**: Multiple questions together
3. **fiction_reading**: Fictional narrative passages
4. **nonfiction_reading**: Informational passages
5. **other**: General educational content (lessons, explanations, activities)

## Metrics

### Required for All Content Types

- **overall** (0.0-1.0, continuous): Holistic quality assessment
  - 0.85-0.98: Acceptable
  - 0.99-1.0: Superior
- **factual_accuracy** (binary): Factually correct
- **educational_accuracy** (binary): Fulfills educational intent

### Content-Specific Metrics

**Question** (11 total metrics):
- curriculum_alignment
- clarity_precision
- reveals_misconceptions
- difficulty_alignment
- passage_reference
- distractor_quality
- stimulus_quality
- mastery_learning_alignment

**Quiz** (8 total metrics):
- concept_coverage
- difficulty_distribution
- non_repetitiveness
- test_preparedness
- answer_balance (computed programmatically)

**Reading Passages** (9 total metrics):
- reading_level_match
- length_appropriateness
- topic_focus
- engagement
- accuracy_and_logic
- question_quality

**Other** (8 total metrics):
- educational_value
- direct_instruction_alignment
- content_appropriateness
- clarity_and_organization
- engagement

All metrics except `overall` are binary (0.0 = fail, 1.0 = pass).

## Output Format

```json
{
  "content_type": "question",
  "overall": {
    "score": 0.92,
    "reasoning": "Detailed explanation...",
    "suggested_improvements": "Specific advice..."
  },
  "factual_accuracy": {
    "score": 1.0,
    "reasoning": "All information is correct..."
  },
  "educational_accuracy": {
    "score": 1.0,
    "reasoning": "Question fulfills its purpose..."
  },
  ... (additional content-specific metrics)
}
```

## Curriculum Support

The system supports parameterized curriculum selection:

```python
# Use default (common_core)
result = await service.evaluate(content)

# Specify curriculum
result = await service.evaluate(content, curriculum="common_core")
```

Curriculum search is handled by the InceptAPI, which maintains the authoritative list of supported curricula and manages vector store access. The API will return a descriptive error if an unsupported curriculum is requested.

To configure the InceptAPI endpoint and API key:
```bash
# Required: API key for InceptAPI authentication
export INCEPT_API_KEY="your-api-key-here"

# Optional: Override the default InceptAPI endpoint
export INCEPTAPI_BASE_URL="https://inceptapi.rp.devfactory.com/api"
```

**Note:** API keys have been required since December 09, 2025. Contact shawn.sullivan@trilogy.com to obtain an API key.

## Extending the System

### Adding a New Evaluator

1. **Create Model** (`models/new_type.py`):
```python
from .base import BaseEvaluationResult, MetricResult

class NewTypeEvaluationResult(BaseEvaluationResult):
    content_type: str = "new_type"
    new_metric: MetricResult = ...
```

2. **Create Prompt** (`prompts/new_type/evaluation.txt`):
```
Your evaluation instructions here...
```

3. **Create Evaluator** (`evaluators/new_type.py`):
```python
class NewTypeEvaluator(BaseEvaluator):
    def _load_prompt(self) -> str:
        # Load from prompts/new_type/evaluation.txt
    
    async def evaluate(self, content, curriculum):
        # Implementation
```

4. **Update Classifier** (`prompts/classifier.txt`):
   - Add new content type to classification options

5. **Update Router** (`router/evaluation_router.py`):
```python
self.evaluators[ContentType.NEW_TYPE] = NewTypeEvaluator()
```

## Testing

```bash
# Run with verbose logging
python -m src.cli --file test_content.txt --verbose

# Test specific content type
python -m src.cli "Your test question here" --output test_results.json

# Validate output format
cat test_results.json | python -m json.tool
```

## API Deployment

See `api/README.md` for comprehensive guide on deploying as REST API using:
- FastAPI (recommended)
- AWS Lambda (serverless)
- AWS EC2 (server-based)
- Docker containers

## Performance

- **Classification**: ~1-3 seconds
- **Evaluation**: ~10-30 seconds (varies by content complexity)
- **Total Pipeline**: ~15-35 seconds per content item

Factors affecting performance:
- Curriculum search (if explicit standards found)
- Object counting (if images present)
- Content length and complexity

## Troubleshooting

### API Key Errors
```
ValueError: OPENAI_API_KEY environment variable is required
```
**Solution**: Create a `.env` file in the project root with your API key:
```bash
OPENAI_API_KEY=your-key-here
```

### Curriculum Not Found
```
ValueError: Curriculum 'xyz' not supported
```
**Solution**: Check available curriculums in `config/settings.py`

### Timeout Errors
**Solution**: Increase timeout in `config/settings.py`

### Image Download Fails
**Solution**: System automatically falls back to direct URLs

## Development

### Code Structure

```
src/
├── models/          # Pydantic data models
├── evaluators/      # Content evaluators
├── classifier/      # Content classification
├── router/          # Evaluation routing
├── tools/           # Utilities (curriculum, images)
├── config/          # Configuration
├── prompts/         # External prompts
├── api/             # Future REST API
├── service.py       # Main orchestration
├── cli.py           # Command-line interface
└── main.py          # Entry point
```

### Logging

```python
import logging
logging.basicConfig(level=logging.INFO)

# Or set via environment
export LOG_LEVEL=DEBUG
```

## License

See LICENSE file in repository root.

## Support

For issues or questions, please refer to the main repository documentation.

