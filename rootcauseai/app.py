"""RootCauseAI - Log Analyzer Agent. AI-powered log analysis tool."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response

from rootcauseai.cache import get_cache
from rootcauseai.cost_tracker import get_cost_tracker
from rootcauseai.exceptions import LLMServiceError, LogAnalysisError
from rootcauseai.analyzer import LogAnalyzer
from rootcauseai.rate_limit import RateLimitMiddleware

# Load environment variables from .env file
load_dotenv()

# Constants

CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200
LLM_TEMPERATURE = 0.2
LLM_MODEL = "gpt-4o-mini"
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"

# Initialize FastAPI app
app = FastAPI(title="RootCauseAI - Log Analyzer Agent", version="0.1.0")

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "10")),
    requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "100")),
    requests_per_day=int(os.getenv("RATE_LIMIT_PER_DAY", "1000")),
)

# Initialize analyzer
analyzer = LogAnalyzer(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    max_concurrent=MAX_CONCURRENT_REQUESTS,
    enable_cache=ENABLE_CACHE,
    preprocess_logs=os.getenv("PREPROCESS_LOGS", "true").lower() == "true",
    filter_debug=os.getenv("FILTER_DEBUG", "true").lower() == "true",
    min_severity=os.getenv("MIN_LOG_SEVERITY", "WARN"),
)


def analyze_logs(log_text: str) -> str:
    """Analyze logs using parallel processing (sync wrapper).

    Args:
        log_text: The log text to analyze.

    Returns:
        Combined analysis of all log chunks.

    Raises:
        LLMServiceError: If LLM service call fails.
        LogAnalysisError: If log analysis fails.
    """
    return analyzer.analyze_logs_sync(log_text, prompt_template=None)


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    """Serve the main HTML page.

    Returns:
        HTML content of the main page.

    Raises:
        HTTPException: If index.html file is not found.
    """
    html_path = Path("index.html")
    try:
        return html_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Frontend file not found: {html_path}",
        ) from e
    except (OSError, UnicodeDecodeError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read frontend file: {str(e)}",
        ) from e


@app.post("/analyze", response_model=None)
async def analyze_log_file(file: UploadFile = File(...)) -> Response:
    """Analyze uploaded log file.

    Args:
        file: The uploaded log file.

    Returns:
        Analysis results or error response.
    """
    if file.filename is None or not file.filename.endswith(".txt"):
        return JSONResponse(
            status_code=400,
            content={"error": "Only .txt log files are supported"},
        )

    try:
        content = await file.read()
        log_text = content.decode("utf-8", errors="ignore")

        if not log_text.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Log file is empty"},
            )

        insights = await analyzer.analyze_logs_parallel(log_text, prompt_template=None)

        return JSONResponse(content={"analysis": insights})

    except (UnicodeDecodeError, ValueError) as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Failed to decode log file: {str(e)}"},
        )
    except (LLMServiceError, LogAnalysisError) as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Analysis failed: {e.message}"},
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "An unexpected error occurred during log analysis"},
        )


@app.get("/health")
async def health_check() -> dict[str, str | bool | dict]:
    """Health check endpoint.

    Returns:
        Health status and configuration information.
    """
    api_key_set = bool(os.getenv("OPENAI_API_KEY"))
    cost_tracker = get_cost_tracker()
    cache = get_cache() if ENABLE_CACHE else None

    response: dict[str, str | bool | dict] = {
        "status": "healthy",
        "openai_api_key_configured": api_key_set,
        "optimization": {
            "cache_enabled": ENABLE_CACHE,
            "parallel_processing": True,
            "max_concurrent": MAX_CONCURRENT_REQUESTS,
        },
    }

    if api_key_set:
        daily_cost = cost_tracker.get_daily_cost()
        monthly_cost = cost_tracker.get_monthly_cost()
        usage_stats = cost_tracker.get_usage_stats(days=7)

        response["costs"] = {
            "daily_usd": round(daily_cost, 4),
            "monthly_usd": round(monthly_cost, 4),
            "average_per_request": round(usage_stats["average_cost_per_request"], 4),
        }

    if cache:
        cache_stats = cache.get_stats()
        response["cache"] = {
            "entries": cache_stats["total_entries"],
            "size_mb": round(cache_stats["total_size_mb"], 2),
        }

    return response


def main() -> None:
    """Main entry point for running the application."""
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
