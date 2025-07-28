# Adobe Hackathon Round 1B - Approach Explanation

## Problem Summary

We were given a collection of PDFs and asked to identify the most relevant sections and subsections based on a specified persona and their job-to-be-done. The output needed to include metadata, top section headings, and relevant textual content, all under CPU-only constraints and within a 60-second execution time.

---

## Our Approach

### 1. PDF Parsing and Outline Extraction
We reused the multilingual and performance-optimized extractor developed in Round 1A (`process_pdfs.py`) to extract hierarchical headings from each document.

### 2. Embedding-based Relevance Ranking
To determine which sections are most relevant to the persona’s task:
- We concatenate the persona and job-to-be-done into a query.
- We encode this query and each extracted section heading using `all-MiniLM-L6-v2` from Sentence Transformers.
- We rank the sections using cosine similarity and select the top 10.

### 3. Subsection Analysis
For each top-ranked section, we extract the full page text from the corresponding page using `PyMuPDF`.

### 4. Output Format
We return a JSON file that includes:
- Input metadata
- Ranked sections
- Subsection-level analysis with refined text

### 5. Technical Stack
- `PyMuPDF` for PDF parsing
- `sentence-transformers` for semantic ranking
- `torch` for inference
- All models are CPU-compatible and < 100MB in size

---

## Constraints Handled
- ✅ Offline: All models and logic run without internet
- ✅ Performance: < 1GB model, CPU-only, < 60s runtime
- ✅ Multilingual and structured extraction

This setup ensures modularity, reusability from Round 1A, and full compliance with challenge guidelines.