"""Log analyzer with parallel processing and caching."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rootcauseai.cache import get_cache
from rootcauseai.cost_tracker import get_cost_tracker
from rootcauseai.exceptions import LLMServiceError
from rootcauseai.log_preprocessor import (
    detect_log_format,
    estimate_log_complexity,
    preprocess_logs,
)

logger = logging.getLogger(__name__)


class LogAnalyzer:
    """Log analyzer with parallel processing and cost-saving features."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.2,
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
        max_concurrent: int = 5,
        enable_cache: bool = True,
        preprocess_logs: bool = True,
        filter_debug: bool = True,
        min_severity: str = "WARN",
    ) -> None:
        """Initialize log analyzer.

        Args:
            model: OpenAI model to use.
            temperature: Model temperature (lower = more deterministic).
            chunk_size: Size of log chunks for parallel processing.
            chunk_overlap: Overlap between chunks to preserve context.
            max_concurrent: Maximum concurrent API requests.
            enable_cache: Enable result caching to reduce API calls.
            preprocess_logs: Enable log preprocessing to filter noise.
            filter_debug: Filter DEBUG level log messages.
            min_severity: Minimum log severity to include (DEBUG, INFO, WARN, ERROR, FATAL).
        """
        self.llm = ChatOpenAI(temperature=temperature, model=model)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self.max_concurrent = max_concurrent
        self.enable_cache = enable_cache
        self.preprocess_logs = preprocess_logs
        self.filter_debug = filter_debug
        self.min_severity = min_severity
        self.cache = get_cache() if enable_cache else None
        self.cost_tracker = get_cost_tracker()
        self.model = model

    async def analyze_chunk_async(
        self,
        chunk: str,
        prompt_template: str,
    ) -> tuple[str, int, int]:
        """Analyze a single chunk asynchronously.

        Args:
            chunk: Log chunk to analyze.
            prompt_template: Prompt template (may contain {log_data}, {log_format}, {complexity}).

        Returns:
            Tuple of (analysis, input_tokens, output_tokens).

        Raises:
            LLMServiceError: If analysis fails.
        """
        try:
            log_format = detect_log_format(chunk)
            complexity = estimate_log_complexity(chunk)
            
            formatted_prompt = prompt_template.format(
                log_data=chunk,
                log_format=log_format,
                complexity=complexity,
            )

            result = await asyncio.to_thread(self.llm.invoke, formatted_prompt)

            # Estimate tokens (rough approximation)
            input_tokens = len(formatted_prompt.split()) * 1.3
            output_tokens = len(result.content.split()) * 1.3

            self.cost_tracker.record_usage(
                model=self.model,
                input_tokens=int(input_tokens),
                output_tokens=int(output_tokens),
            )

            return result.content, int(input_tokens), int(output_tokens)

        except Exception as e:
            raise LLMServiceError(
                f"Failed to analyze log chunk: {str(e)}",
                original_error=e,
            ) from e

    async def analyze_logs_parallel(
        self,
        log_text: str,
        prompt_template: str | None = None,
    ) -> str:
        """Analyze logs with parallel processing.

        Args:
            log_text: The log text to analyze.
            prompt_template: Optional prompt template. If None, selects optimal prompt.

        Returns:
            Combined analysis of all log chunks.
        """
        if self.preprocess_logs:
            original_length = len(log_text)
            log_text = preprocess_logs(
                log_text,
                filter_debug=self.filter_debug,
                min_severity=self.min_severity,
            )
            filtered_length = len(log_text)
            if original_length != filtered_length:
                reduction = ((original_length - filtered_length) / original_length) * 100
                logger.info(
                    f"Log preprocessing: {original_length} -> {filtered_length} chars "
                    f"({reduction:.1f}% reduction)",
                )

        if self.enable_cache and self.cache:
            cached_result = self.cache.get(log_text)
            if cached_result:
                logger.info("Returning cached analysis result")
                return cached_result

        if prompt_template is None:
            from rootcauseai.prompts import get_prompt_for_logs

            log_format = detect_log_format(log_text)
            prompt_template = get_prompt_for_logs(log_text, log_format)
            logger.info(f"Selected prompt for {log_format} format logs")

        chunks = self.splitter.split_text(log_text)

        if not chunks:
            return "No log content to analyze."

        logger.info(f"Analyzing {len(chunks)} chunks with max {self.max_concurrent} concurrent requests")

        semaphore = asyncio.Semaphore(self.max_concurrent)
        tasks = []

        async def analyze_with_semaphore(chunk: str) -> tuple[str, int, int]:
            async with semaphore:
                return await self.analyze_chunk_async(chunk, prompt_template)

        for chunk in chunks:
            tasks.append(analyze_with_semaphore(chunk))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        combined_analysis: list[str] = []
        total_input_tokens = 0
        total_output_tokens = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing chunk {i}: {result}")
                combined_analysis.append(f"[Error analyzing chunk {i + 1}: {str(result)}]")
            else:
                analysis, input_tokens, output_tokens = result
                combined_analysis.append(analysis)
                total_input_tokens += input_tokens
                total_output_tokens += output_tokens

        final_analysis = "\n\n".join(combined_analysis)

        if self.enable_cache and self.cache:
            self.cache.set(log_text, final_analysis)

        logger.info(
            f"Analysis complete: {total_input_tokens} input tokens, "
            f"{total_output_tokens} output tokens",
        )

        return final_analysis

    def analyze_logs_sync(
        self,
        log_text: str,
        prompt_template: str | None = None,
    ) -> str:
        """Synchronous wrapper for async analysis.

        Args:
            log_text: The log text to analyze.
            prompt_template: Optional prompt template. If None, selects optimal prompt.

        Returns:
            Combined analysis of all log chunks.
        """
        return asyncio.run(self.analyze_logs_parallel(log_text, prompt_template))
