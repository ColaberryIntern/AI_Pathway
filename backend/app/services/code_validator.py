"""Code Validator — tests Python code examples and auto-fixes failures.

Runs each Python code example from generated lesson content through a subprocess,
catches errors, and attempts LLM-based auto-repair (up to 2 retries).
"""
import asyncio
import logging
import re

logger = logging.getLogger(__name__)

# Packages available in both the server Python env and Pyodide browser sandbox
ALLOWED_IMPORTS = {
    "numpy", "pandas", "scipy", "matplotlib", "scikit-learn", "sklearn",
    "sympy", "regex", "requests", "json", "csv", "math", "random",
    "datetime", "collections", "itertools", "functools", "os", "sys",
    "io", "re", "string", "textwrap", "statistics", "pathlib",
    "base64", "hashlib", "urllib",
}

# Code that makes network calls or writes files — skip validation for safety
_SKIP_PATTERNS = re.compile(
    r'\b(?:requests\.(?:get|post|put|delete|patch)|urllib\.request\.urlopen|'
    r'open\s*\([^)]*["\']w|subprocess|os\.system)\b',
    re.IGNORECASE,
)


async def _test_run_python(code: str, timeout: int = 10) -> str | None:
    """Run Python code in a subprocess and return error string or None on success."""
    if _SKIP_PATTERNS.search(code):
        return None  # Skip validation for network/file code

    # Prepend matplotlib backend for headless execution
    preamble = "import matplotlib; matplotlib.use('agg')\n" if "matplotlib" in code or "plt" in code else ""
    full_code = preamble + code

    try:
        proc = await asyncio.create_subprocess_exec(
            "python", "-c", full_code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        if proc.returncode != 0:
            return stderr.decode("utf-8", errors="replace").strip()
        return None
    except asyncio.TimeoutError:
        proc.kill()
        return None  # Timeout is OK — may be intentional (e.g., sleep/loop)
    except Exception as e:
        logger.warning("Code validation subprocess error: %s", e)
        return None  # Don't block lesson generation on validation infra issues


async def _fix_code_with_llm(code: str, error: str, llm_generate) -> str | None:
    """Ask the LLM to fix a broken code example. Returns fixed code or None."""
    prompt = f"""Fix this Python code example that has an error. Return ONLY the corrected Python code, nothing else.

RULES:
- Only use standard library + numpy, pandas, scikit-learn, matplotlib, scipy, sympy, requests
- Do NOT use transformers, torch, tensorflow, openai, langchain, or any package requiring native compilation
- Keep the same teaching purpose and structure
- If the code makes network calls, use a public test API (e.g., jsonplaceholder.typicode.com)

BROKEN CODE:
```python
{code}
```

ERROR:
{error}

Return only the fixed Python code (no markdown fences, no explanation):"""

    try:
        fixed = await llm_generate(
            prompt=prompt,
            temperature=0.2,
            max_tokens=2048,
        )
        # Strip markdown code fences if present
        fixed = fixed.strip()
        if fixed.startswith("```"):
            fixed = re.sub(r"^```(?:python)?\n?", "", fixed)
            fixed = re.sub(r"\n?```$", "", fixed)
        return fixed.strip() if len(fixed.strip()) > 10 else None
    except Exception as e:
        logger.warning("LLM code fix failed: %s", e)
        return None


async def validate_and_fix_code_examples(content: dict, llm_generate) -> dict:
    """Test-run Python code examples and auto-fix failures.

    Args:
        content: Lesson content dict with 'code_examples' array
        llm_generate: Async callable for LLM generation (e.g., llm.generate)

    Returns:
        Updated content dict with fixed code examples
    """
    code_examples = content.get("code_examples", [])
    if not code_examples:
        return content

    for i, example in enumerate(code_examples):
        if example.get("language", "python").lower() != "python":
            continue

        code = example.get("code", "")
        if not code or len(code) < 10:
            content["code_examples"][i]["validated"] = False
            continue

        # Skip validation for network/file I/O code — can't guarantee it works in Pyodide
        if _SKIP_PATTERNS.search(code):
            content["code_examples"][i]["validated"] = False
            continue

        error = await _test_run_python(code)
        if not error:
            content["code_examples"][i]["validated"] = True
            continue

        logger.info("Code example %d (%s) failed: %s", i, example.get("title", ""), error[:200])

        # Attempt fix (up to 2 retries)
        for attempt in range(2):
            fixed_code = await _fix_code_with_llm(code, error, llm_generate)
            if not fixed_code:
                break
            # Test the fix
            new_error = await _test_run_python(fixed_code)
            if not new_error:
                logger.info("Code example %d fixed on attempt %d", i, attempt + 1)
                content["code_examples"][i]["code"] = fixed_code
                content["code_examples"][i]["validated"] = True
                break
            error = new_error  # Try again with new error
            code = fixed_code
        else:
            logger.warning("Code example %d could not be auto-fixed", i)
            content["code_examples"][i]["validated"] = False

    return content
