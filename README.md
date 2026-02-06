# RootCauseAI

**Log Analyzer Agent**

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checking: MyPy](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](http://mypy.readthedocs.io/)
[![Testing: Pytest](https://img.shields.io/badge/testing-pytest-blue.svg)](https://docs.pytest.org/)

An AI-powered log analysis tool built with LangChain and OpenAI that automatically identifies errors, explains root causes, and suggests fixes for your application logs.

## Features

- **Simple Upload Interface** - Drag and drop or select log files
- **AI-Powered Analysis** - Uses GPT-4o-mini to understand log context
- **Root Cause Detection** - Identifies the most likely causes of failures
- **Actionable Insights** - Get practical next steps to fix issues
- **Pattern Recognition** - Spots repeated issues and suspicious patterns
- **Fast & Modern** - Built with FastAPI and modern Python tooling
- **Well Tested** - Comprehensive test suite with pytest
- **Type Safe** - Full type hints with MyPy checking
- **Cost Efficient** - Parallel processing, caching, and rate limiting

## Architecture

The application consists of:
- **Backend**: FastAPI server with LangChain for LLM orchestration
- **Frontend**: Modern HTML/JavaScript UI with TailwindCSS
- **LLM**: OpenAI GPT-4o-mini for log analysis
- **Tooling**: Ruff (linting/formatting), MyPy (type checking), Pytest (testing)

## Quick Start

### Prerequisites

- Python 3.11 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/rootcauseai.git
   cd rootcauseai
   ```

2. **Install uv** (if not already installed):
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Or via pip
   pip install uv
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```
   This automatically creates a virtual environment and installs all dependencies.

4. **Set up environment variables:**
   ```bash
   cp .env.example .env  # If .env.example exists
   # Or create .env manually
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

5. **Run the application:**
   ```bash
   # Development mode (with auto-reload)
   uv run uvicorn rootcauseai.app:app --reload --host 0.0.0.0 --port 8000
   
   # Or use the entry point
   uv run rootcauseai
   ```

The application will be available at: **http://localhost:8000**

### Alternative Setup with pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -e ".[dev]"

# Run the application
uvicorn rootcauseai.app:app --reload --host 0.0.0.0 --port 8000
```

## Usage

1. Open your browser and navigate to `http://localhost:8000`
2. Click "Choose Log File" and select a `.txt` log file (or drag and drop)
3. Click "Analyze Logs"
4. Wait for the AI to process your logs (usually 10-30 seconds)
5. Review the analysis results with identified errors, root causes, and suggested fixes

### Testing with Sample Logs

A sample log file is included in `samples/sample_log.txt`. You can use this to test the application:

1. Start the server
2. Upload `samples/sample_log.txt`
3. Review the analysis

## API Endpoints

### `GET /`
Returns the main HTML interface

### `POST /analyze`
Analyzes an uploaded log file

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (text/plain, `.txt` extension required)

**Response:**
```json
{
  "analysis": "Detailed analysis of the logs..."
}
```

**Error Responses:**
- `400`: Invalid file type or empty file
- `429`: Rate limit exceeded
- `500`: Server error during analysis

### `GET /health`
Health check endpoint with cost and cache statistics

**Response:**
```json
{
  "status": "healthy",
  "openai_api_key_configured": true,
  "optimization": {
    "cache_enabled": true,
    "parallel_processing": true,
    "max_concurrent": 5
  },
  "costs": {
    "daily_usd": 0.0234,
    "monthly_usd": 0.7012,
    "average_per_request": 0.0023
  },
  "cache": {
    "entries": 15,
    "size_mb": 0.45
  }
}
```

## Development

### Project Structure

```
rootcauseai/
├── rootcauseai/          # Main package
│   ├── __init__.py
│   ├── app.py           # FastAPI application
│   ├── cache.py         # Response caching
│   ├── cost_tracker.py  # Cost tracking
│   ├── exceptions.py    # Custom exceptions
│   ├── analyzer.py  # Parallel processing and analysis
│   └── rate_limit.py    # Rate limiting middleware
├── tests/               # Test suite
│   ├── conftest.py     # Pytest fixtures
│   └── test_app.py     # Application tests
├── samples/             # Sample log files
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=rootcauseai --cov-report=html

# Run specific test file
uv run pytest tests/test_app.py

# Run with verbose output
uv run pytest -v
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Type check
uv run mypy rootcauseai
```

### Adding Dependencies

```bash
# Add a runtime dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Remove a dependency
uv remove package-name
```

## Deployment

### Production Considerations

1. **Environment Variables:**
   - Set `OPENAI_API_KEY` in your production environment
   - Use a secret management service (AWS Secrets Manager, HashiCorp Vault, etc.)
   - Configure rate limits: `RATE_LIMIT_PER_MINUTE`, `RATE_LIMIT_PER_HOUR`, `RATE_LIMIT_PER_DAY`
   - Set concurrency: `MAX_CONCURRENT_REQUESTS`
   - Enable caching: `ENABLE_CACHE=true`

2. **Rate Limiting:**
   - Built-in rate limiting middleware (configurable)
   - Prevents cost overruns and abuse

3. **File Size Limits:**
   - Configure maximum file upload size in FastAPI
   - Consider streaming for very large files

4. **Error Handling:**
   - Set up proper logging (structured logging recommended)
   - Configure error tracking (Sentry, Rollbar, etc.)

5. **Monitoring:**
   - Add health check monitoring
   - Set up metrics collection (Prometheus, Datadog, etc.)
   - Monitor costs via `/health` endpoint

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml ./
COPY rootcauseai/ ./rootcauseai/
COPY index.html ./

# Install dependencies
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run application
CMD ["uv", "run", "uvicorn", "rootcauseai.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Heroku Deployment

The project includes a `Procfile` for Heroku deployment:

```
web: uvicorn rootcauseai.app:app --host 0.0.0.0 --port $PORT
```

Set the `OPENAI_API_KEY` config var in Heroku:
```bash
heroku config:set OPENAI_API_KEY=your-key-here
```

## Configuration

### Adjusting Chunk Size

Edit constants in `rootcauseai/app.py`:

```python
CHUNK_SIZE = 2000      # Adjust chunk size
CHUNK_OVERLAP = 200    # Adjust overlap
```

### Changing the AI Model

Edit the LLM initialization in `rootcauseai/app.py`:

```python
LLM_MODEL = "gpt-4o-mini"  # Change to "gpt-4o", "gpt-3.5-turbo", etc.
LLM_TEMPERATURE = 0.2       # Adjust creativity (0.0-1.0)
```

### Modifying the Analysis Prompt

The AI prompt system has been enhanced with research-backed optimizations:

- **Structured Prompting**: Uses LogPrompt framework principles (380.7% improvement over simple prompts)
- **Chain-of-Thought Reasoning**: Systematic root cause analysis using "5 Whys" technique
- **Context-Aware Selection**: Automatically selects optimal prompt based on log complexity
- **Log Preprocessing**: Filters noise (DEBUG messages, empty lines) to reduce token usage
- **Format Detection**: Detects log format (JSON, syslog, Apache/Nginx, structured) for better context

Prompts are defined in `rootcauseai/prompts.py`. The system automatically selects the best prompt based on log characteristics. You can customize prompts there if needed.

### Cost Optimization Settings

Configure in `.env`:

```bash
# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100
RATE_LIMIT_PER_DAY=1000

# Parallel Processing
MAX_CONCURRENT_REQUESTS=5

# Caching
ENABLE_CACHE=true
```

## Security

- **Never commit your OpenAI API key** to version control
- Use environment variables or secret management services in production
- Built-in rate limiting prevents abuse
- Validate and sanitize uploaded files
- Set appropriate CORS policies if needed
- Use HTTPS in production
- Consider adding authentication/authorization for production use

## Troubleshooting

### "OpenAI API key not configured"
Make sure you've set the `OPENAI_API_KEY` environment variable before starting the server.

### "Module not found" errors
Ensure you've installed all dependencies:
```bash
uv sync
# or
pip install -e ".[dev]"
```

### Analysis takes too long
For very large log files, consider:
- Reducing `CHUNK_SIZE` in `rootcauseai/app.py`
- Using a faster model (e.g., `gpt-3.5-turbo`)
- Pre-filtering logs to only include ERROR/WARN lines
- Increasing `MAX_CONCURRENT_REQUESTS` for faster parallel processing

### Port already in use
Change the port:
```bash
uv run uvicorn rootcauseai.app:app --reload --port 8001
```

### Rate limit errors
Adjust rate limits in `.env` or check `/health` endpoint for current usage.

## How It Works

1. **File Upload**: User uploads a `.txt` log file through the web interface
2. **Text Splitting**: Large logs are split into chunks (2000 characters with 200 character overlap)
3. **Parallel Processing**: Multiple chunks are analyzed concurrently for faster results
4. **LLM Analysis**: Each chunk is analyzed by GPT-4o-mini using a specialized prompt
5. **Caching**: Results are cached to avoid re-analyzing identical logs
6. **Results Aggregation**: Individual analyses are combined into a comprehensive report
7. **Display**: Results are shown in the web interface

## Cost Optimization

The application includes several cost optimization features:

- **Parallel Processing**: Faster analysis with concurrent API calls
- **Response Caching**: Avoids re-analyzing identical log content (70-90% savings)
- **Rate Limiting**: Prevents cost overruns
- **Cost Tracking**: Automatic tracking of API usage and costs
- **Token Optimization**: Efficient chunking and processing

See `COST_OPTIMIZATION.md` for detailed information.

## Roadmap

Potential enhancements:
- **Vector Search**: Use embeddings for very large log files
- **Historical Analysis**: Store and compare past incidents
- **Log Type Detection**: Adapt prompts for different log formats (nginx, apache, etc.)
- **Real-time Streaming**: Analyze logs as they're generated
- **Multi-file Support**: Analyze multiple log files together
- **Export Results**: Download analysis as PDF or JSON
- **Authentication**: User authentication and authorization
- **Database**: Store analysis history

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks:
   ```bash
   uv run ruff format .
   uv run ruff check .
   uv run mypy rootcauseai
   uv run pytest
   ```
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide (enforced by Ruff)
- Add type hints to all functions
- Write tests for new features
- Update documentation as needed
- Keep commits focused and atomic

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LangChain](https://www.langchain.com/) - LLM orchestration
- [OpenAI](https://openai.com/) - GPT models
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- [Ruff](https://docs.astral.sh/ruff/) - Fast Python linter and formatter
- [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS framework

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/rootcauseai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/rootcauseai/discussions)

---

Made with care by the RootCauseAI contributors
