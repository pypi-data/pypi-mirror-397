import json
import os
import re
import asyncio
import logging
from pathlib import Path
from typing import Optional, Sequence, Union

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    # Remove synchronous requests fallback logic
    print("Warning: httpx module not found. Please install it via 'pip install httpx'")

from tqdm import tqdm

REMOTE_MODEL_URL = os.environ.get(
    "LLM_PREDICTOR_API_URL", "https://api.siliconflow.cn/v1/chat/completions"
)
REMOTE_MODEL_NAME = os.environ.get("LLM_PREDICTOR_MODEL", "deepseek-ai/DeepSeek-V3")
REMOTE_API_TIMEOUT = float(os.environ.get("LLM_PREDICTOR_API_TIMEOUT", "30"))
MAX_CONCURRENT_REQUESTS = int(os.environ.get("LLM_PREDICTOR_MAX_CONCURRENT", "10"))
BATCH_SIZE = int(os.environ.get("LLM_PREDICTOR_BATCH_SIZE", "20"))
DEBUG_BATCH = os.environ.get("LLM_PREDICTOR_DEBUG_BATCH", "").strip() in ("1", "true", "True")
MAX_RETRIES = int(os.environ.get("LLM_PREDICTOR_MAX_RETRIES", "5"))
RETRY_BASE_SECONDS = float(os.environ.get("LLM_PREDICTOR_RETRY_BASE_SECONDS", "0.8"))
CONFIG_PATH_CANDIDATES = [
    Path(__file__).resolve().parent.parent / "config" / "api_keys.json",
    Path.cwd() / "config" / "api_keys.json",
]
_API_KEY_CACHE: Optional[str] = None


def _load_api_key_from_config() -> Optional[str]:
    for path in CONFIG_PATH_CANDIDATES:
        if not path.exists():
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            api_key = data.get("llm_predictor_api_key") or data.get("deepseek_api_key")
            if api_key and not api_key.lower().startswith("your_"):
                return api_key
        except (OSError, ValueError) as err:
            print(f"Failed to read configuration file {path}: {err}")
    return None


def _resolve_api_key() -> Optional[str]:
    global _API_KEY_CACHE
    if _API_KEY_CACHE:
        return _API_KEY_CACHE

    for env_var in ("LLM_PREDICTOR_API_KEY", "DEEPSEEK_API_KEY"):
        api_key = os.environ.get(env_var)
        if api_key and not api_key.lower().startswith("your_"):
            _API_KEY_CACHE = api_key
            return api_key

    api_key = _load_api_key_from_config()
    if api_key:
        _API_KEY_CACHE = api_key
    return api_key


def _build_api_payload(text_input: str) -> dict:
    """Build API request payload"""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a precise noise detector for DOM text segments. "
                "Reply using only a single digit: '1' keeps the text, '0' discards it."
            ),
        },
        {
            "role": "user",
            "content": (
                "Perform three-step noise detection:\n"
                "1. Content analysis (determine if the snippet is irrelevant).\n"
                "2. Tag risk analysis (consider last_tag and risk_tags metadata).\n"
                "3. Structural verification (depth and confidence).\n"
                "Only respond with 0 or 1 for the following snippet:\n"
                f"{text_input}"
            ),
        },
    ]
    return {
        "model": REMOTE_MODEL_NAME,
        "messages": messages,
        "stream": False,
        "max_tokens": 8,
        "temperature": 0.1,
        "top_p": 0.9,
        "top_k": 50,
        "n": 1,
        "response_format": {"type": "text"},
    }


def _build_batch_api_payload(text_inputs: Sequence[str]) -> dict:
    """Build a single API request payload that predicts multiple items at once."""
    formatted_items: list[str] = []
    for idx, text_input in enumerate(text_inputs):
        formatted_items.append(f"ITEM {idx}:\n{text_input}")

    user_content = (
        f"You will be given {len(text_inputs)} snippets.\n"
        "For each snippet, perform the same three-step noise detection as usual.\n"
        "Return ONLY a JSON array of integers (0/1) with the same length, "
        "where element i is the decision for ITEM i.\n"
        "Do not include code fences, keys, or any extra text.\n\n"
        + "\n\n---\n\n".join(formatted_items)
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a precise noise detector for DOM text segments. "
                "Output must be a strict JSON array of 0/1 decisions."
            ),
        },
        {"role": "user", "content": user_content},
    ]
    return {
        "model": REMOTE_MODEL_NAME,
        "messages": messages,
        "stream": False,
        "max_tokens": 256,
        "temperature": 0.1,
        "top_p": 0.9,
        "top_k": 50,
        "n": 1,
        "response_format": {"type": "text"},
    }


def _parse_batch_decisions(content: str, expected_len: int) -> list[Union[int, str]]:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content).strip()

    parsed: object
    try:
        parsed = json.loads(content)
    except Exception:
        parsed = None

    decisions: list[Union[int, str]] = []
    if isinstance(parsed, list):
        for value in parsed:
            if value in (0, 1):
                decisions.append(int(value))
            elif isinstance(value, str) and value.strip() in ("0", "1"):
                decisions.append(int(value.strip()))
            else:
                decisions.append("error")
    elif isinstance(parsed, dict):
        for key in ("decisions", "results", "labels"):
            value = parsed.get(key)
            if isinstance(value, list):
                for item in value:
                    if item in (0, 1):
                        decisions.append(int(item))
                    elif isinstance(item, str) and item.strip() in ("0", "1"):
                        decisions.append(int(item.strip()))
                    else:
                        decisions.append("error")
                break

    if not decisions:
        digits = re.findall(r"[01]", content)
        decisions = [int(digit) for digit in digits]

    if len(decisions) < expected_len:
        decisions.extend(["error"] * (expected_len - len(decisions)))
    elif len(decisions) > expected_len:
        decisions = decisions[:expected_len]
    return decisions


async def call_remote_model_api_async(
    text_input: str, 
    api_key: Optional[str] = None,
    client: Optional[object] = None
) -> Union[int, str]:
    """Asynchronously call remote LLM API for noise detection"""
    api_key = api_key or _resolve_api_key()
    if not api_key:
        print("Missing remote LLM API key, please set LLM_PREDICTOR_API_KEY or DEEPSEEK_API_KEY.")
        return "error"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = _build_api_payload(text_input)

    try:
        if HAS_HTTPX and client is not None:
            # Use httpx async client
            response = await client.post(
                REMOTE_MODEL_URL,
                json=payload,
                headers=headers,
                timeout=REMOTE_API_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            
            content = (
                result.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            for char in content:
                if char in ("0", "1"):
                    return int(char)
            print(f"Remote API returned incorrect format: {content}")
            return "error"
        else:
            print("Error: httpx not installed or client not provided, cannot execute async request")
            return "error"
    except Exception as e:
        tqdm.write(f"[llm_predictor] Remote API request error: {e}")
        return "error"


async def call_remote_model_api_batch_async(
    text_inputs: Sequence[str],
    api_key: Optional[str] = None,
    client: Optional[object] = None,
) -> list[Union[int, str]]:
    """Asynchronously call remote LLM API for multiple snippets in one request."""
    if not text_inputs:
        return []

    api_key = api_key or _resolve_api_key()
    if not api_key:
        print("Missing remote LLM API key, please set LLM_PREDICTOR_API_KEY or DEEPSEEK_API_KEY.")
        return ["error"] * len(text_inputs)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = _build_batch_api_payload(text_inputs)

    if not (HAS_HTTPX and client is not None):
        print("Error: httpx not installed or client not provided, cannot execute async request")
        return ["error"] * len(text_inputs)

    last_error: Optional[BaseException] = None
    for attempt in range(max(1, MAX_RETRIES) + 1):
        try:
            if DEBUG_BATCH:
                tqdm.write(
                    f"[llm_predictor] sending batch request: size={len(text_inputs)} "
                    f"(attempt {attempt}/{max(1, MAX_RETRIES) + 1})"
                )
            response = await client.post(
                REMOTE_MODEL_URL,
                json=payload,
                headers=headers,
                timeout=REMOTE_API_TIMEOUT,
            )
            response.raise_for_status()
            result = response.json()

            content = (
                result.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            return _parse_batch_decisions(content, expected_len=len(text_inputs))
        except Exception as e:
            last_error = e

            status_code: Optional[int] = None
            retry_after: Optional[float] = None
            if HAS_HTTPX:
                if isinstance(e, httpx.HTTPStatusError):
                    status_code = e.response.status_code
                    ra = e.response.headers.get("Retry-After")
                    if ra:
                        try:
                            retry_after = float(ra)
                        except ValueError:
                            retry_after = None

            should_retry = status_code in (408, 409, 425, 429, 500, 502, 503, 504) or status_code is None
            if attempt >= max(1, MAX_RETRIES) + 1 or not should_retry:
                tqdm.write(f"[llm_predictor] Remote API request error: {e}")
                return ["error"] * len(text_inputs)

            sleep_seconds = retry_after if retry_after is not None else (RETRY_BASE_SECONDS * (2 ** (attempt - 1)))
            sleep_seconds = min(max(0.1, sleep_seconds), 20.0)
            if DEBUG_BATCH:
                tqdm.write(
                    f"[llm_predictor] retrying after {sleep_seconds:.2f}s "
                    f"(status={status_code})"
                )
            await asyncio.sleep(sleep_seconds)

    tqdm.write(f"[llm_predictor] Remote API request error: {last_error}")
    return ["error"] * len(text_inputs)


async def process_predictions_async(
    input_json_path: str, 
    output_json_path: str,
    max_concurrent: Optional[int] = None,
    api_key: Optional[str] = None
):
    """Asynchronously batch process prediction tasks"""
    max_concurrent = max_concurrent or MAX_CONCURRENT_REQUESTS
    
    if not HAS_HTTPX:
        print("Error: httpx library must be installed to use async processing feature. Please run 'pip install httpx'")
        return

    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if os.path.exists(output_json_path):
        with open(output_json_path, "r", encoding="utf-8") as f:
            results = json.load(f)
    else:
        results = {}
    
    # Use provided api_key, or try to resolve from environment/config
    if api_key is None:
        api_key = _resolve_api_key()
    if not api_key:
        print("Warning: Missing remote LLM API key. Using default predictions (keeping all text segments).")
        # Create default predictions (all 1, meaning keep all text) when no API key is available
        if not data:
            print("Warning: Input data is empty. Creating empty prediction results.")
            results = {}
        else:
            for file_name, entries in data.items():
                if file_name in results:
                    continue
                results[file_name] = [
                    {
                        "text": item.get("text", ""),
                        "path": item.get("path", ""),
                        "prediction": 1  # Default: keep all text when no API key
                    }
                    for item in entries
                ]
        # Save default predictions
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Default predictions saved to {output_json_path}")
        return
    
    # Create httpx async client
    async with httpx.AsyncClient(timeout=REMOTE_API_TIMEOUT) as client:
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_batch_with_semaphore(batch_items):
            async with semaphore:
                inputs = [item.get("input", "") for item in batch_items]
                predictions = await call_remote_model_api_batch_async(inputs, api_key, client)
                updated = []
                for item, prediction in zip(batch_items, predictions):
                    updated.append(
                        {
                            "text": item.get("text", ""),
                            "path": item.get("path", ""),
                            "prediction": prediction,
                        }
                    )
                return updated
        
        for file_name, entries in tqdm(data.items(), desc="Processing files"):
            if file_name in results:
                print(f"Skipping {file_name} as it has already been processed.")
                continue
            
            # Create progress bar
            pbar = tqdm(total=len(entries), desc=f"Processing entries in {file_name}", leave=False)
            
            batch_size = max(1, BATCH_SIZE)
            batches = [entries[i : i + batch_size] for i in range(0, len(entries), batch_size)]
            if DEBUG_BATCH:
                tqdm.write(
                    f"[llm_predictor] file={file_name} entries={len(entries)} "
                    f"batch_size={batch_size} requests={len(batches)} max_concurrent={max_concurrent}"
                )

            async def process_batch_with_progress(batch_items):
                result = await process_batch_with_semaphore(batch_items)
                pbar.update(len(batch_items))
                return result
            
            tasks = [process_batch_with_progress(batch) for batch in batches]
            batched_entries = await asyncio.gather(*tasks)
            pbar.close()
            
            updated_entries = [item for batch in batched_entries for item in batch]
            results[file_name] = updated_entries
            # Save immediately after processing each file
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)


def process_predictions(input_json_path: str, output_json_path: str, api_key: Optional[str] = None):
    """
    Batch process prediction tasks (async only)
    
    Args:
        input_json_path: Input JSON file path
        output_json_path: Output JSON file path
        api_key: Optional API key. If not provided, will be resolved from environment variables or config file
    """
    if not HAS_HTTPX:
        print("Error: httpx library must be installed. Please run 'pip install httpx'")
        return
        
    # Force use of async processing
    asyncio.run(process_predictions_async(input_json_path, output_json_path, api_key=api_key))


def main():
    folder_path = r"/home/ubuntu/Webis/samples/output_basic"
    input_json = os.path.join(folder_path, "dataset", "extra_datasets.json")
    output_json = os.path.join(folder_path, "dataset", "pred_results.json")
    process_predictions(input_json, output_json)


if __name__ == "__main__":
    main()
    
