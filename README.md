# Docsentinel

**Evidence-first document QA with auditable citation verification.**

Docsentinel is a research-oriented prototype for checking whether an AI-generated claim is traceable to the document evidence it cites. Its first vertical slice implements deterministic quote-existence and provenance checks before adding semantic entailment models or an LLM answerer.

> Current status: working, dependency-free verification MVP. This repository does **not** yet claim semantic entailment or end-to-end LLM QA.

## Why Docsentinel?

A citation can look convincing while pointing to the wrong passage—or to text that does not exist. Docsentinel makes the first part of that problem testable:

1. Require each claim to include a source chunk ID and a verbatim quote.
2. Normalize harmless text-format differences.
3. Check whether the quote occurs in the cited chunk.
4. If not, search the rest of the retrieved evidence to detect misattribution.
5. Abstain when evidence provenance cannot be established.

The key distinction: **quote existence is not the same as semantic support**. A quote can exist and still fail to support a claim. That is why the current MVP reports `QUOTE_VERIFIED`, not `SUPPORTED`.

## Quickstart

Requires Python 3.10+; no third-party packages are needed.

```bash
git clone https://github.com/whiterose456/Docsentinel.git
cd Docsentinel

python -m docsentinel demo
python -m unittest discover -s tests -v
```

Verify your own structured answer:

```bash
python -m docsentinel verify --input examples/verification_case.json
```

Input format:

```json
{
  "question": "When does the agreement terminate?",
  "chunks": [
    {
      "chunk_id": "contract::p4::c1",
      "text": "The agreement shall terminate on 31 December 2027."
    }
  ],
  "claims": [
    {
      "text": "The agreement ends on 31 December 2027.",
      "chunk_id": "contract::p4::c1",
      "quote": "The agreement shall terminate on 31 December 2027."
    }
  ]
}
```

## Current verdicts

| Verdict | Meaning |
|---|---|
| `QUOTE_VERIFIED` | Normalized quote exists in the cited chunk. Provenance is verified; semantic support is not. |
| `MISATTRIBUTED` | Quote is absent from the cited chunk but exists in another retrieved chunk. |
| `QUOTE_NOT_FOUND` | Quote cannot be found in any retrieved chunk. |
| `UNATTRIBUTED` | Claim has no usable quote or chunk ID. |

The decision layer abstains if there are no claims or any claim fails provenance verification. This is intentionally conservative.

## Architecture (current vertical slice)

```text
Structured answer + retrieved chunks
                |
                v
        Input validation
                |
                v
   L1: normalized quote matching
       |                  |
       | cited chunk      | other retrieved chunk
       v                  v
 QUOTE_VERIFIED       MISATTRIBUTED
                          |
                 no match anywhere
                          v
                    QUOTE_NOT_FOUND
                |
                v
       Claim-level verdicts
                |
                v
     Answer / abstain decision
                |
                v
       JSON audit report
```

## Normalization policy

The matcher applies Unicode NFKC normalization, removes soft hyphens, standardizes curly quotation marks and en/em dashes, collapses whitespace, trims, and case-folds. It does not reorder words, alter numbers, or join non-contiguous spans.

This deliberately favors traceability over permissive fuzzy matching. A legitimate paraphrase may not match; that is a known limitation, not evidence that the underlying claim is false.

## 12-hour prototype scope

- [x] Deterministic quote-existence check
- [x] Wrong-chunk / misattribution detection
- [x] Explicit abstention decision
- [x] JSON CLI and reproducible demo
- [x] Unit tests for normalization and verdicts
- [x] Structured audit output
- [ ] Dense + BM25 hybrid retrieval
- [ ] LLM answer generation with structured output
- [ ] MiniCheck semantic entailment verification
- [ ] Frozen evaluation set and baseline study
- [ ] Streamlit interface and latency/cost report

## Next engineering milestones

1. Add ingestion and chunk metadata (document, page, character offsets).
2. Add dense + BM25 retrieval with a shared chunk set.
3. Add an answerer adapter that emits claim-level quotes.
4. Add a semantic verifier behind an interface; calibrate it against human labels.
5. Compare conventional RAG, quote-required generation, and the full verifier on a frozen test set.
6. Report coverage, selective risk, false abstention, provenance errors, latency, and cost.

## Important limitations

- A matching quote proves only that the text exists in the cited chunk.
- It does not prove entailment, factual truth, causality, or that a model relied on the quote.
- No LLM, retriever, PDF parser, or semantic NLI model is included in this first slice.
- Results are corpus-bounded: source documents themselves may be incorrect.
- Normalization is designed primarily for English/Latin-script text.

## Project positioning

Docsentinel is an experimental reliability layer for document-grounded AI—not a production legal, financial, or medical advice system. The immediate research question is whether auditable claim-level provenance checks, followed by calibrated semantic verification, can reduce unsupported answers at an acceptable coverage and latency cost.

## License

MIT. Dataset and model licenses must be checked separately before redistribution.
