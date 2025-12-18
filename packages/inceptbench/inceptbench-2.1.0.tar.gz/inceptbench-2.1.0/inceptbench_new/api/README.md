# Educational Content Evaluator REST API

Production-ready FastAPI application for evaluating educational content across multiple quality dimensions.

## Features

- ✅ **FastAPI** - Modern, fast, async Python web framework
- ✅ **Automatic OpenAPI docs** - Interactive API documentation at `/docs`
- ✅ **Lambda-ready** - Mangum adapter for AWS Lambda deployment
- ✅ **Docker-ready** - Dockerfile and docker-compose for containerized deployment
- ✅ **Type-safe** - Full Pydantic integration for request/response validation
- ✅ **Production middleware** - CORS, timing headers, error handling
- ✅ **Health checks** - `/health` endpoint for monitoring
- ✅ **Comprehensive logging** - Structured logging for debugging

## API Endpoints

### `POST /evaluate`
Evaluate educational content and get structured quality assessment.

**Accepts two input formats:**

1. **Simple string content:**
```json
{
  "content": "What is the capital of France?",
  "curriculum": "common_core",
  "generation_prompt": "Generate a geography question (optional)"
}
```

2. **Structured content array:**
```json
{
  "generated_content": [
    {
      "id": "q1",
      "request": {
        "grade": "7",
        "subject": "mathematics",
        "type": "mcq",
        "difficulty": "medium",
        "locale": "en-US",
        "skills": {
          "lesson_title": "Solving Linear Equations",
          "substandard_id": "CCSS.MATH.7.EE.A.1",
          "substandard_description": "Solve linear equations"
        },
        "instruction": "Create a linear equation problem"
      },
      "content": {
        "question": "What is the value of x in 3x + 7 = 22?",
        "answer": "C",
        "answer_explanation": "Subtract 7, then divide by 3",
        "answer_options": [
          {"key": "A", "text": "3"},
          {"key": "B", "text": "4"},
          {"key": "C", "text": "5"},
          {"key": "D", "text": "6"}
        ],
        "image_url": ["https://example.com/img1.png"],
        "additional_details": "Optional details"
      }
    }
  ]
}
```

**Content Types:**
- `mcq` - Multiple choice questions (requires `answer_options` array)
- `fill-in` - Fill in the blank questions (no answer_options)
- `article` - Reading passages and articles

**Response (v2.0):**
```json
{
  "request_id": "uuid-here",
  "evaluations": {
    "q1": {
      "inceptbench_new_evaluation": {
        "content_type": "question",
        "overall": {
          "score": 0.85,
          "reasoning": "...",
          "suggested_improvements": "..."
        },
        "factual_accuracy": {...},
        "educational_accuracy": {...},
        "curriculum_alignment": {...},
        "weighted_score": 0.8387
      },
      "score": 0.85
    }
  },
  "evaluation_time_seconds": 12.34,
  "inceptbench_version": "x.y.z",
  "failed_items": null
}
```

**Partial Success Response (when some items fail):**
```json
{
  "request_id": "uuid-here",
  "evaluations": {
    "q1": {
      "inceptbench_new_evaluation": {...},
      "score": 0.85
    }
  },
  "evaluation_time_seconds": 12.34,
  "inceptbench_version": "x.y.z",
  "failed_items": [
    {"item_id": "q2", "error": "Invalid content format"},
    {"item_id": "q3", "error": "Curriculum validation failed"}
  ]
}
```

**Performance & Error Handling:**
- All items processed in parallel (1 or 100 items - same speed!)
- If an item fails, evaluation continues for remaining items
- Successful evaluations returned in `evaluations`
- Failed items listed in `failed_items` (null if all succeeded)

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "Educational Content Evaluator"
}
```

### `GET /curriculums`
List available curriculum standards.

**Response:**
```json
{
  "curriculums": ["common_core"],
  "default": "common_core"
}
```

### `GET /`
API information and endpoint listing.

## Local Development

### Prerequisites
- Python 3.11+
- OpenAI API key
- Anthropic API key (for object counting)

### Setup

1. **Install dependencies:**
```bash
pip install -r src/requirements.txt
pip install -r src/api/requirements.txt
```

2. **Configure environment variables:**
```bash
# .env file in project root
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
INCEPTBENCH_API_KEY=your-api-key-1,your-api-key-2  # Comma-separated list of client API keys
```

**Generate API keys:**
```bash
# Single key
python3 -c "import secrets; print('INCEPTBENCH_API_KEY=' + secrets.token_urlsafe(32))"

# Multiple keys (comma-separated)
python3 -c "import secrets; print('INCEPTBENCH_API_KEY=' + secrets.token_urlsafe(32) + ',' + secrets.token_urlsafe(32))"
```

3. **Run development server:**
```bash
# From project root
uvicorn src.api.main:app --reload

# Or use the convenience script
python -m src.api.main
```

4. **Access the API:**
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing the API

**Using curl:**
```bash
# Health check
curl http://localhost:8000/health

# List curriculums
curl http://localhost:8000/curriculums

# Evaluate simple content
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What is 2 + 2?",
    "curriculum": "common_core"
  }'

# Evaluate structured MCQ
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "generated_content": [{
      "id": "q1",
      "request": {
        "grade": "5",
        "subject": "mathematics",
        "type": "mcq",
        "difficulty": "easy",
        "locale": "en-US",
        "skills": {
          "lesson_title": "Basic Addition",
          "substandard_id": "CCSS.MATH.5.NBT.B.7",
          "substandard_description": "Add decimals"
        },
        "instruction": "Create an addition problem"
      },
      "content": {
        "question": "What is 2 + 2?",
        "answer": "B",
        "answer_explanation": "2 + 2 equals 4",
        "answer_options": [
          {"key": "A", "text": "3"},
          {"key": "B", "text": "4"},
          {"key": "C", "text": "5"}
        ]
      }
    }]
  }'
```

**Using Python:**
```python
import requests

# Simple content
response = requests.post(
    "http://localhost:8000/evaluate",
    json={
        "content": "What is 2 + 2?",
        "curriculum": "common_core"
    }
)

result = response.json()
print(f"Request ID: {result['request_id']}")
first_eval = list(result['evaluations'].values())[0]
print(f"Overall score: {first_eval['score']}")

# Structured content
response = requests.post(
    "http://localhost:8000/evaluate",
    json={
        "generated_content": [{
            "id": "q1",
            "request": {
                "grade": "7",
                "subject": "mathematics",
                "type": "mcq",
                "difficulty": "medium",
                "locale": "en-US",
                "skills": {
                    "lesson_title": "Linear Equations",
                    "substandard_id": "CCSS.MATH.7.EE.A.1",
                    "substandard_description": "Solve linear equations"
                },
                "instruction": "Create equation problem"
            },
            "content": {
                "question": "Solve: 3x + 7 = 22",
                "answer": "C",
                "answer_explanation": "x = 5",
                "answer_options": [
                    {"key": "A", "text": "3"},
                    {"key": "B", "text": "4"},
                    {"key": "C", "text": "5"}
                ]
            }
        }]
    }
)

result = response.json()
print(f"Score for q1: {result['evaluations']['q1']['score']}")
```

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Build and run:**
```bash
docker-compose up --build
```

2. **Access the API:**
- http://localhost:8000

3. **Stop:**
```bash
docker-compose down
```

### Using Docker directly

1. **Build image:**
```bash
docker build -t edu-evaluator-api .
```

2. **Run container:**
```bash
docker run -p 8000:8000 --env-file .env edu-evaluator-api
```

## AWS Lambda Deployment

### Prerequisites
- AWS CLI configured
- AWS SAM CLI installed
- S3 bucket for deployment artifacts

### Deployment Steps

1. **Install SAM CLI:**
```bash
pip install aws-sam-cli
```

2. **Build the Lambda package:**
```bash
sam build
```

3. **Deploy (first time):**
```bash
sam deploy --guided
```

Follow the prompts:
- Stack Name: `edu-evaluator-api`
- AWS Region: `us-east-1` (or your preferred region)
- OpenAI API Key: `your-openai-key`
- Anthropic API Key: `your-anthropic-key`
- Stage: `prod` (or `dev`, `staging`)

4. **Deploy (subsequent):**
```bash
sam deploy
```

5. **Get API URL:**
```bash
aws cloudformation describe-stacks \
  --stack-name edu-evaluator-api \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

### Lambda Configuration Notes

- **Timeout:** 300 seconds (5 minutes) - Evaluations can take time
- **Memory:** 2048 MB (2 GB) - Needed for LLM processing
- **Handler:** `src.api.lambda_handler.lambda_handler`
- **Runtime:** Python 3.11

### Lambda Limitations

⚠️ **Be aware of:**
- Cold starts (first request may be slow)
- Maximum timeout of 15 minutes
- Provisioned concurrency recommended for production
- Consider Step Functions for very long evaluations

## EC2 Deployment

### Setup

1. **Launch EC2 instance:**
- AMI: Amazon Linux 2023 or Ubuntu 22.04
- Instance type: t3.medium or larger
- Security group: Allow inbound on port 80/443

2. **Install dependencies:**
```bash
# Update system
sudo yum update -y  # Amazon Linux
# or
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Install Python 3.11
sudo yum install python3.11 -y  # Amazon Linux
# or
sudo apt install python3.11 python3.11-venv -y  # Ubuntu

# Install Docker (optional)
sudo yum install docker -y && sudo systemctl start docker
```

3. **Clone repository:**
```bash
git clone <your-repo> /opt/edu-evaluator
cd /opt/edu-evaluator
```

4. **Setup Python environment:**
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r src/requirements.txt
pip install -r src/api/requirements.txt
```

5. **Configure environment:**
```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
INCEPTBENCH_API_KEY=your-api-key-1,your-api-key-2
LOG_LEVEL=INFO
EOF
```

6. **Run with systemd:**
```bash
# Create service file
sudo cat > /etc/systemd/system/edu-evaluator.service << EOF
[Unit]
Description=Educational Content Evaluator API
After=network.target

[Service]
Type=notify
User=ec2-user
WorkingDirectory=/opt/edu-evaluator
Environment="PATH=/opt/edu-evaluator/venv/bin"
ExecStart=/opt/edu-evaluator/venv/bin/gunicorn \
    src.api.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 300
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable edu-evaluator
sudo systemctl start edu-evaluator
```

7. **Setup Nginx reverse proxy (optional but recommended):**
```bash
sudo yum install nginx -y
sudo systemctl enable nginx

# Configure Nginx
sudo cat > /etc/nginx/conf.d/edu-evaluator.conf << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
    }
}
EOF

sudo systemctl restart nginx
```

## Monitoring and Logging

### CloudWatch (Lambda)
- Logs automatically sent to CloudWatch
- View in AWS Console → CloudWatch → Log Groups → `/aws/lambda/edu-evaluator-api`

### Application Logs
```bash
# Docker
docker-compose logs -f api

# Systemd (EC2)
sudo journalctl -u edu-evaluator -f

# Direct (development)
# Logs print to stdout/stderr
```

### Metrics to Monitor
- Request rate
- Error rate
- Response time (in `X-Process-Time` header)
- LLM API call latency
- Memory usage
- API key usage/costs

## Security

### Production Checklist

- [ ] Configure CORS for specific origins (not `*`)
- [ ] Add API key authentication
- [ ] Enable HTTPS only
- [ ] Set up rate limiting
- [ ] Configure request size limits
- [ ] Rotate API keys regularly
- [ ] Use AWS Secrets Manager for sensitive data (Lambda)
- [ ] Enable CloudWatch alarms for errors
- [ ] Set up WAF rules (if using API Gateway)
- [ ] Review and harden security groups

### API Key Authentication

API key authentication is already implemented! The API uses Bearer token authentication.

**Setup:**
```bash
# In .env file
INCEPTBENCH_API_KEY=key1,key2,key3  # Comma-separated list
```

**Usage:**
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Authorization: Bearer your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"content": "What is 2+2?"}'
```

**Multiple Keys:**
Each valid key in the comma-separated list will be accepted. This allows:
- Multiple teams/users with different keys
- Key rotation without downtime
- Separate keys for different environments

## Performance Optimization

### Caching
Consider adding caching for repeated content:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
async def evaluate_cached(content_hash: str, curriculum: str):
    # ... evaluation logic
```

### Concurrency
- Uvicorn: Single worker, async
- Gunicorn: Multiple workers, use `--workers` flag
- Lambda: Automatically concurrent

### Recommended Workers
- **Development:** 1 worker (Uvicorn)
- **Production (EC2):** `(2 * CPU cores) + 1` workers
- **Lambda:** Configured by concurrent executions

## Troubleshooting

### Common Issues

**Issue:** Import errors when running API
```bash
# Solution: Ensure you're running from project root
cd /path/to/inceptbench
uvicorn src.api.main:app
```

**Issue:** Timeout errors on evaluation
```bash
# Solution: Increase timeout in deployment config
# Gunicorn: --timeout 600
# Lambda: Timeout: 600 in template.yaml
```

**Issue:** Memory errors in Lambda
```bash
# Solution: Increase memory allocation in template.yaml
MemorySize: 3008  # Maximum for Lambda
```

**Issue:** CORS errors in browser
```bash
# Solution: Configure CORS properly in src/api/main.py
allow_origins=["https://yourdomain.com"]
```

## Cost Estimates

### Lambda (per million requests)
- API Gateway: ~$3.50
- Lambda compute: ~$0.20 per GB-second
- LLM API calls: Variable (depends on usage)

### EC2 (monthly)
- t3.medium: ~$30/month
- Load balancer (optional): ~$16/month
- Data transfer: Variable

## Next Steps

- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Add request caching
- [ ] Set up CI/CD pipeline
- [ ] Add integration tests
- [ ] Configure monitoring dashboards
- [ ] Set up alerts
- [ ] Load testing
- [ ] Documentation updates
