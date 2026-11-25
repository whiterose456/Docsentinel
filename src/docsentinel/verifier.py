"""Deterministic quote existence and provenance verification.

Important: a matching quote proves textual existence, not semantic entailment.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any


def normalize_text(value: str) -> str:
    """Normalize formatting noise without changing lexical content."""
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("\u00ad", "")
    value = re.sub(r"[\u2018\u2019\u201b]", "'", value)
    value = re.sub(r"[\u201c\u201d]", '"', value)
    value = re.sub(r"[\u2013\u2014]", "-", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip().casefold()


def _validate_payload(payload: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON object.")
    chunks = payload.get("chunks")
    claims = payload.get("claims")
    if not isinstance(chunks, list) or not isinstance(claims, list):
        raise ValueError("'chunks' and 'claims' must both be arrays.")

    seen_ids: set[str] = set()
    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            raise ValueError(f"chunks[{index}] must be an object.")
        chunk_id, text = chunk.get("chunk_id"), chunk.get("text")
        if not isinstance(chunk_id, str) or not chunk_id.strip():
            raise ValueError(f"chunks[{index}].chunk_id must be a non-empty string.")
        if chunk_id in seen_ids:
            raise ValueError(f"Duplicate chunk_id: {chunk_id}")
        if not isinstance(text, str):
            raise ValueError(f"chunks[{index}].text must be a string.")
        seen_ids.add(chunk_id)

    for index, claim in enumerate(claims):
        if not isinstance(claim, dict) or not isinstance(claim.get("text"), str):
            raise ValueError(f"claims[{index}] must contain a string 'text'.")
    return chunks, claims


def verify_claim(claim: dict[str, Any], chunks: list[dict]) -> dict[str, Any]:
    """Verify quote existence in the cited chunk and then the retrieved set."""
    quote = claim.get("quote")
    cited_id = claim.get("chunk_id")
    claim_text = claim.get("text", "")

    base = {"claim": claim_text, "cited_chunk_id": cited_id, "quote": quote}
    if not isinstance(quote, str) or not quote.strip() or not isinstance(cited_id, str) or not cited_id.strip():
        return {**base, "verdict": "UNATTRIBUTED", "matched_chunk_id": None,
                "l1_pass": False, "detail": "Claim is missing a usable quote or chunk_id."}

    normalized_quote = normalize_text(quote)
    chunk_by_id = {chunk["chunk_id"]: chunk for chunk in chunks}
    cited_chunk = chunk_by_id.get(cited_id)

    if cited_chunk and normalized_quote in normalize_text(cited_chunk["text"]):
        return {**base, "verdict": "QUOTE_VERIFIED", "matched_chunk_id": cited_id,
                "l1_pass": True,
                "detail": "Quote exists in the cited chunk; semantic support has not been evaluated."}

    for chunk in chunks:
        if chunk["chunk_id"] != cited_id and normalized_quote in normalize_text(chunk["text"]):
            return {**base, "verdict": "MISATTRIBUTED", "matched_chunk_id": chunk["chunk_id"],
                    "l1_pass": False,
                    "detail": "Quote exists in another retrieved chunk, not the cited chunk."}

    return {**base, "verdict": "QUOTE_NOT_FOUND", "matched_chunk_id": None,
            "l1_pass": False,
            "detail": "Quote was not found in any retrieved chunk."}


def verify_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and verify every claim, then apply a conservative abstention rule."""
    chunks, claims = _validate_payload(payload)
    results = [verify_claim(claim, chunks) for claim in claims]
    all_provenance_verified = bool(results) and all(
        result["verdict"] == "QUOTE_VERIFIED" for result in results
    )
    return {
        "question": payload.get("question", ""),
        "decision": "RETURN_WITH_PROVENANCE" if all_provenance_verified else "ABSTAIN",
        "abstained": not all_provenance_verified,
        "claim_count": len(results),
        "verified_claim_count": sum(r["verdict"] == "QUOTE_VERIFIED" for r in results),
        "claims": results,
        "verification_scope": "L1 quote existence and chunk provenance only; semantic entailment is not evaluated.",
    }
