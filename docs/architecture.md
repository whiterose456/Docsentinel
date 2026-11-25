# Architecture and verification contract

## Scope of this iteration

This implementation is the deterministic L1/provenance slice of the proposed QuoteCheck approach. It deliberately does not label a claim semantically supported. The output verdict `QUOTE_VERIFIED` means only that the normalized quote occurs in the chunk identified by the claim.

## Data flow

1. The caller supplies retrieved chunks and claim-level citations as JSON.
2. Input validation rejects malformed structures and duplicate chunk IDs.
3. The verifier normalizes the quote and candidate chunk text using the documented policy.
4. It checks the cited chunk first.
5. If the quote is absent there, it scans the remaining retrieved chunks.
6. It emits a claim-level verdict and a conservative answer/abstain decision.

## Safety and interpretation

- `QUOTE_VERIFIED` is not a factuality or entailment judgment.
- `MISATTRIBUTED` identifies a provenance mismatch, not necessarily a false claim.
- `QUOTE_NOT_FOUND` can include legitimate paraphrases and chunk-boundary cases.
- `ABSTAIN` means the system cannot establish the required citation provenance under this policy.

## Extension points

A future semantic verifier should accept (claim, quote, surrounding source context) and return a calibrated score plus a thresholded decision. Its precision/recall and false-accept/false-reject rates must be measured against human labels before its verdict is allowed to influence the final answer.
