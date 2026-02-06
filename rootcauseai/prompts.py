"""Prompts for log analysis using best practices from prompt engineering research.

Based on research:
- LogPrompt framework: 380.7% improvement over simple prompts
- Structured prompting: Better interpretability and accuracy
- Chain-of-thought reasoning: Improved root cause identification
"""

from __future__ import annotations

# Enhanced prompt template based on LogPrompt framework and structured prompting best practices
# Research shows structured prompts improve LLM performance by up to 380.7% for log analysis
# This prompt uses chain-of-thought reasoning and structured output format

LOG_ANALYSIS_PROMPT_TEMPLATE = """You are an expert Site Reliability Engineer with 10+ years of experience in root cause analysis, incident response, and system debugging.

## Your Task
Analyze the provided application logs using systematic root cause analysis methodology. Your goal is to identify errors, determine underlying causes, and provide actionable remediation steps.

## Analysis Methodology

Apply this structured, step-by-step approach:

### Step 1: Error Identification & Categorization
- Scan logs chronologically for all errors, exceptions, warnings, and failures
- Categorize by severity: FATAL > ERROR > WARN > INFO
- Count error frequencies to identify patterns
- Note timestamps and sequence of events
- Identify any error cascades or dependencies

### Step 2: Pattern Recognition
- Group similar errors together
- Identify repeating patterns (same error multiple times)
- Look for temporal patterns (errors at specific times)
- Detect correlation between different error types
- Note any anomalies or unusual sequences

### Step 3: Root Cause Analysis (Use Chain-of-Thought)
For each critical error, reason through:
1. What is the immediate symptom? (the error message)
2. What component/service is failing? (identify the source)
3. Why is it failing? (underlying cause - not just the error)
4. What conditions led to this? (contributing factors)
5. Is this a symptom of a deeper issue? (cascading failure analysis)

Apply the "5 Whys" technique: Keep asking "why" until you reach the fundamental cause.

### Step 4: Impact Assessment
- Service availability impact (downtime, degraded performance)
- Data integrity concerns (corruption, loss, inconsistency)
- User experience impact (errors visible to end users)
- Business impact (revenue, SLA violations, reputation)
- Affected components and dependencies

### Step 5: Remediation Plan
Provide prioritized, actionable steps:

**IMMEDIATE (0-15 minutes):**
- Steps to restore service or prevent further damage
- Quick workarounds or rollbacks
- Emergency mitigations

**SHORT-TERM (15 minutes - 2 hours):**
- Proper fixes to resolve root causes
- Configuration changes
- Code hotfixes if needed
- Service restarts or redeployments

**LONG-TERM (2+ hours):**
- Architectural improvements
- Code refactoring
- Infrastructure changes
- Process improvements

### Step 6: Prevention & Monitoring
- Monitoring improvements (what metrics/alerts to add)
- Preventive measures (how to avoid recurrence)
- Early warning signs (indicators to watch for)
- Testing recommendations (how to catch this earlier)

## Output Format

Structure your response exactly as follows:

**=== CRITICAL ERRORS ===**
[List all FATAL and ERROR level issues with timestamps]

**=== ERROR PATTERNS ===**
[Grouped patterns and frequencies]

**=== ROOT CAUSE ANALYSIS ===**
[Primary root causes with chain-of-thought reasoning]
- Root Cause 1: [explanation]
  - Why: [reasoning]
  - Evidence: [log excerpts]
- Root Cause 2: [if multiple]

**=== IMPACT ASSESSMENT ===**
[Service, data, and user impact]

**=== IMMEDIATE ACTIONS ===**
[Prioritized steps to take now]
1. [Action with specific command/config if applicable]
2. [Next action]

**=== INVESTIGATION STEPS ===**
[How to verify and gather more information]

**=== REMEDIATION PLAN ===**
- Immediate: [steps]
- Short-term: [fixes]
- Long-term: [improvements]

**=== PREVENTION RECOMMENDATIONS ===**
[Monitoring, alerting, and process improvements]

## Guidelines

- Be precise and evidence-based: Reference specific log lines when making claims
- Use technical terminology correctly: Match the technology stack visible in logs
- Prioritize by severity: Address FATAL/ERROR before WARN
- Be actionable: Provide specific commands, configs, or code changes
- If information is insufficient: Clearly state what additional logs/metrics are needed
- Avoid speculation: Base all conclusions on evidence present in the logs
- Be concise: Focus on the most critical issues first

## Log Context
- Format: {log_format}
- Complexity: {complexity}

## Log Data

{log_data}

Begin your systematic analysis:"""

# Quick error detection prompt (uses fewer tokens)
QUICK_ERROR_DETECTION_PROMPT = """You are a log analysis expert. Quickly identify critical errors and their root causes.

Analyze these logs and provide:
1. Critical errors (FATAL/ERROR level)
2. Most likely root cause (one sentence)
3. Immediate fix (one actionable step)

Logs:
{log_data}

Response format:
ERRORS: [list]
ROOT CAUSE: [explanation]
FIX: [action]"""

# Detailed analysis prompt for complex incidents
DETAILED_ANALYSIS_PROMPT = """You are a senior SRE conducting a comprehensive post-incident analysis.

Perform an in-depth analysis following this methodology:

1. **Timeline Reconstruction**: Create a precise chronological sequence of events with timestamps
2. **Error Chain Mapping**: Map how errors relate, cascade, and propagate through the system
3. **Root Cause Analysis**: Use 5 Whys technique to identify primary and contributing causes
4. **Impact Assessment**: Quantify business, technical, and user impact
5. **Remediation Procedures**: Provide detailed, step-by-step fix procedures with rollback plans
6. **Prevention Strategy**: Suggest monitoring, alerting, testing, and architectural improvements

Log Format: {log_format}
Complexity: {complexity}

Logs:
{log_data}

Provide a comprehensive incident report with executive summary, technical details, and actionable recommendations."""

# Context-aware prompt selector
def get_prompt_for_logs(log_text: str, log_format: str = "standard") -> str:
    """Select prompt based on log characteristics.

    Args:
        log_text: Log text to analyze.
        log_format: Detected log format.

    Returns:
        Appropriate prompt template with placeholders for {log_data}, {log_format}, {complexity}.
    """
    from rootcauseai.log_preprocessor import estimate_log_complexity

    complexity = estimate_log_complexity(log_text)

    # Use detailed prompt for complex incidents
    if complexity == "complex":
        # Return template with placeholders - will be filled in analyze_chunk_async
        return DETAILED_ANALYSIS_PROMPT

    # Use standard prompt for moderate/simple complexity
    # Standard prompt doesn't use log_format/complexity, but we'll add them for consistency
    return LOG_ANALYSIS_PROMPT_TEMPLATE
