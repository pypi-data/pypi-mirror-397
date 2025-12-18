# veriskgo/langchain_tracker.py
"""
LangChain-specific tracking decorator.
Provides enhanced extraction for LangChain response objects.
"""

from __future__ import annotations

import functools
import inspect
from typing import Any, Dict, Optional

from .core.usage import build_usage_payload, empty_usage_payload, UsageData
from .core.decorators import create_span_wrapper, SpanContext
from .trace_manager import serialize_value


# ============================================================
# LANGCHAIN-SPECIFIC EXTRACTORS
# ============================================================

def _extract_lc_callback_usage(args, kwargs) -> Dict[str, int]:
    """
    Extract token usage from LangChain callback objects in args/kwargs.
    """
    usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    def scan(obj):
        if obj is None:
            return

        if hasattr(obj, "prompt_tokens") or hasattr(obj, "completion_tokens"):
            usage["input_tokens"] = getattr(obj, "prompt_tokens", 0)
            usage["output_tokens"] = getattr(obj, "completion_tokens", 0)
            usage["total_tokens"] = getattr(
                obj, "total_tokens",
                usage["input_tokens"] + usage["output_tokens"],
            )
            return

        if isinstance(obj, dict):
            for v in obj.values():
                scan(v)

        if isinstance(obj, (list, tuple)):
            for v in obj:
                scan(v)

    scan(args)
    scan(kwargs)
    return usage


def _extract_lc_text(result: Any) -> str:
    """
    Extract text from LangChain response objects.
    """
    # Case 1: StrOutputParser returns str
    if isinstance(result, str):
        return result

    # Case 2: Pipeline returns tuple like (summary, keywords)
    if isinstance(result, tuple) and len(result) >= 1:
        return result[0]

    # Case 3: ChatModel response with .content attribute
    if not isinstance(result, (str, dict, list, tuple)) and hasattr(result, "content"):
        return result.content

    # Case 4: Fallback - serialize
    return serialize_value(result)


def _extract_lc_model(result: Any) -> Optional[str]:
    """
    Extract model name from LangChain response metadata.
    """
    meta = getattr(result, "response_metadata", None)
    if isinstance(meta, dict):
        return meta.get("model")
    return None


def _extract_lc_usage_from_result(result: Any, callback_usage: Dict[str, int]) -> Dict[str, int]:
    """
    Extract usage from LangChain result, with callback fallback.
    """
    # Prefer callback usage if available
    if callback_usage.get("total_tokens", 0) > 0:
        return callback_usage

    # Try response_metadata
    meta = getattr(result, "response_metadata", None)
    if isinstance(meta, dict):
        return {
            "input_tokens": meta.get("input_tokens", 0),
            "output_tokens": meta.get("output_tokens", 0),
            "total_tokens": (
                meta.get("input_tokens", 0) + meta.get("output_tokens", 0)
            ),
        }

    return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}


# ============================================================
# LANGCHAIN FINALIZATION
# ============================================================

def _finalize_langchain_span(
    ctx: SpanContext,
    result: Any,
    args: tuple,
    kwargs: dict,
) -> Dict[str, Any]:
    """
    Finalize LangChain span with usage/cost data.
    """
    # Get bedrock usage if available (from observer)
    from .llm import _get_bedrock_usage
    bedrock_payload = _get_bedrock_usage()
    if bedrock_payload:
        return bedrock_payload
    
    # Extract from LangChain callbacks/metadata
    callback_usage = _extract_lc_callback_usage(args, kwargs)
    usage = _extract_lc_usage_from_result(result, callback_usage)
    model = _extract_lc_model(result)
    
    if usage.get("total_tokens", 0) > 0:
        return build_usage_payload(usage, model_id=model)
    
    return empty_usage_payload(model_id=model)


# ============================================================
# DECORATOR: track_langchain
# ============================================================

def track_langchain(
    name: str = "langchain_call",
    *,
    tags: Optional[Dict[str, Any]] = None,
    capture_locals: bool = True,
    capture_self: bool = True,
):
    """
    LangChain-specific generation decorator.
    
    Enhanced extraction for:
    - LangChain callback token usage
    - response_metadata from ChatModels
    - Text extraction from various output types
    
    Usage:
        @track_langchain()
        async def summarize(text):
            return await chain.ainvoke({"text": text})
            
        @track_langchain(name="qa_chain")
        def answer_question(question):
            return chain.invoke({"question": question})
    """
    def decorator(func):
        return create_span_wrapper(
            func,
            span_name=name or func.__name__,
            span_type="generation",
            capture_locals=capture_locals,
            capture_self=capture_self,
            tags=tags or {},
            finalize_fn=_finalize_langchain_span,
        )
    
    return decorator
