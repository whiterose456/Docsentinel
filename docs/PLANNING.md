# DocSentinel — Project Planning

## 1. Project Overview

**DocSentinel** is an evidence-first document question-answering reliability prototype with an interactive citation-verification demo. It checks whether claims in a structured answer can be traced to the document evidence they cite.

The project is being developed incrementally. The current MVP implements deterministic L1 verification of quotation existence and source-chunk attribution. It does **not** perform semantic entailment verification or establish factual truth.

## 2. Objectives

- Check whether a supplied verbatim quotation exists in the retrieved evidence.
- Verify that the quotation is attributed to the correct source chunk.
- Detect unsupported quotations and missing attribution.
- Produce transparent claim-level verdicts and a machine-readable audit report.
- Abstain when provenance verification fails.
- Establish an extensible foundation for retrieval and semantic verification experiments.

## 3. Current MVP Scope — L1 Verification

### Implemented capabilities

| Component | Current capability | Status |
|---|---|---|
| Structured input | Accepts an answer and retrieved source chunks | Built |
| Input validation | Validates the verification payload | Built |
| Text normalization | Normalizes text before comparison | Built |
| Quote matching | Checks normalized quote existence | Built |
| Attribution checking | Detects quotes found in a different supplied chunk | Built |
| Verdict classification | Emits four provenance verdicts | Built |
| Claim-level reporting | Associates verdicts with individual claims | Built |
| Abstention gate | Abstains when there are no claims or any claim fails provenance verification | Built |
| Audit output | Produces structured JSON audit output | Built |
| CLI and examples | Reproducible command-line demo and example payloads | Built |
| Streamlit interface | Interactive inspection of claims, verdicts, and source chunks | Built |
| Unit tests | Tests normalization and verification behavior | Built |

### Current verdicts

- `QUOTE_VERIFIED`: The normalized quotation exists in the cited source chunk. This verifies provenance, not semantic support.
- `MISATTRIBUTED`: The quotation is absent from the cited chunk but exists in another retrieved chunk.
- `QUOTE_NOT_FOUND`: The quotation cannot be found in any supplied retrieved chunk.
- `UNATTRIBUTED`: The claim has no usable quotation or source chunk ID.

### Explicit scope boundaries

The current MVP does not include:

- PDF parsing or automated document ingestion.
- Dense vector retrieval or BM25 retrieval.
- LLM-based answer generation.
- Semantic entailment or contradiction detection.
- A frozen, human-labelled evaluation benchmark.

A matching quote establishes only that the text exists in the cited chunk. It does not establish that the quote supports the claim, that the claim is true, or that a model relied on that evidence.

## 4. Development Roadmap

The following items are planned extensions; they are not represented as implemented MVP capabilities.

### Phase 1 — PDF Ingestion and Provenance

**Goal:** Process source documents and preserve traceable evidence locations.

Planned work:
- Extract text from PDF documents.
- Split extracted text into source chunks.
- Preserve document identifiers, page numbers, and character offsets where available.
- Maintain chunk provenance through downstream processing.

**Expected outcome:** Documents can be converted into traceable evidence chunks suitable for retrieval and verification.

### Phase 2 — Hybrid Retrieval

**Goal:** Retrieve relevant evidence from ingested documents.

Planned work:
- Add dense vector retrieval.
- Add BM25 lexical retrieval.
- Combine retrieval results using a hybrid strategy.
- Preserve source IDs and metadata in retrieved results.
- Evaluate retrieval quality using a fixed query set.

**Expected outcome:** The system can supply relevant, attributable evidence to the answer-generation stage.

### Phase 3 — LLM Answer Generation

**Goal:** Generate document-grounded answers in a format that can be inspected by DocSentinel.

Planned work:
- Integrate an LLM using retrieved chunks as context.
- Require structured claim-level output.
- Require source chunk identifiers and verbatim quotations.
- Pass generated output through the existing L1 provenance gate.
- Measure answer quality, latency, and cost.

**Expected outcome:** Generated answers can be checked by the existing deterministic verification core.

### Phase 4 — Semantic Entailment Verification

**Goal:** Evaluate whether cited evidence actually supports each associated claim.

Planned work:
- Introduce a semantic entailment model or verification component.
- Distinguish supporting, contradicting, and insufficient evidence.
- Combine semantic assessment with deterministic quote and attribution checks.
- Evaluate semantic verification errors and calibration.
- Retain explicit abstention for insufficient or conflicting evidence.

**Expected outcome:** Verification extends beyond quote existence to assess the relationship between evidence and claims.

### Phase 5 — Evaluation and Baseline Study

**Goal:** Measure whether the evidence-first workflow improves reliability and at what operational cost.

Planned work:
- Build a frozen evaluation set from documents and human-labelled claims.
- Compare conventional answers with ordinary citations, quote-required answers, and quote-required answers gated by DocSentinel.
- Report citation precision, unsupported-claim rate, false abstention, answer coverage, latency, and cost.
- Document dataset construction, limitations, and reproducibility.

Bundled synthetic examples are useful for demonstrations and tests, but should not be presented as a benchmark.

## 5. What to Evaluate Next

The next meaningful step is to establish a small, frozen, human-labelled evaluation set before expanding the system.

| Area | Evaluation question | Candidate metrics |
|---|---|---|
| Quote verification | Does L1 correctly identify quote existence? | Quote verification precision and recall |
| Attribution | Does L1 detect wrong source-chunk references? | Attribution accuracy / F1 |
| Retrieval | Are relevant passages present in the retrieved set? | Recall@K, Precision@K |
| Semantic verification | Does evidence support or contradict a claim? | Entailment precision, recall, F1 |
| Abstention | Does the system abstain on unsupported answers without rejecting too many supported ones? | Unsupported-answer rate, false-abstention rate |
| End-to-end behavior | Does the workflow improve answer reliability? | Citation precision, answer coverage |
| Operations | What is the cost of verification? | Latency and cost per query |

For an initial study, compare:
1. Conventional answers with ordinary citations.
2. Quote-required answers.
3. Quote-required answers plus DocSentinel's provenance gate.

Keep the evaluation documents and labels fixed across conditions so that results are comparable.

## 6. Expected Direction

DocSentinel is intended to evolve from a deterministic provenance-verification core into an evidence-grounded QA reliability pipeline:

1. **Current:** L1 quote-existence and source-attribution verification.
2. **Planned:** PDF ingestion and traceable chunking.
3. **Planned:** Dense and BM25 hybrid retrieval.
4. **Planned:** Structured, evidence-grounded LLM answer generation.
5. **Planned:** Semantic entailment verification and expanded evaluation.

The deterministic L1 layer remains valuable as an independently testable check, even after semantic verification is introduced.
