import os
import json
from datetime import datetime
from process_pdfs import OptimizedMultilingualPDFExtractor
from sentence_transformers import SentenceTransformer, util
import fitz

class PersonaDrivenAnalyzer:
    def __init__(self):
        self.extractor = OptimizedMultilingualPDFExtractor()
        self.embedder = SentenceTransformer(
            "/app/local_model",
            cache_folder="/app/local_model",
            use_auth_token=False
        )

    def load_documents(self, input_dir):
        return [f for f in os.listdir(input_dir) if f.endswith('.pdf')]

    def extract_sections(self, input_dir):
        output = {}
        for fname in self.load_documents(input_dir):
            doc_path = os.path.join(input_dir, fname)
            output[fname] = self.extractor.extract_pdf_structure(doc_path)

        return output

    def rank_sections(self, outlines, persona, job):
        query = f"{persona}. Task: {job}"
        q_embed = self.embedder.encode(query, convert_to_tensor=True)

        section_scores = []
        for doc, entries in outlines.items():
            for item in entries['outline']:
                section = item['text']
                s_embed = self.embedder.encode(section, convert_to_tensor=True)
                score = util.pytorch_cos_sim(q_embed, s_embed).item()
                section_scores.append({
                    "document": doc,
                    "page_number": item["page"],
                    "section_title": section,
                    "importance_rank": 0,
                    "score": score
                })
        section_scores.sort(key=lambda x: -x['score'])
        for i, sec in enumerate(section_scores):
            sec['importance_rank'] = i + 1
            del sec['score']
        return section_scores[:10]

    def extract_subsections(self, section_scores, input_dir):
        results = []
        for sec in section_scores:
            doc = fitz.open(os.path.join(input_dir, sec['document']))
            page = doc[sec['page_number'] - 1]
            results.append({
                "document": sec['document'],
                "page_number": sec['page_number'],
                "section_title": sec['section_title'],
                "refined_text": page.get_text()
            })
        return results

    def run(self, input_dir, output_dir, persona, job):
        outlines = self.extract_sections(input_dir)
        ranked_sections = self.rank_sections(outlines, persona, job)
        refined = self.extract_subsections(ranked_sections, input_dir)
        result = {
            "input_documents": list(outlines.keys()),
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "extracted_sections": ranked_sections,
            "sub_section_analysis": refined
        }
        with open(os.path.join(output_dir, "output.json"), "w") as f:
            json.dump(result, f, indent=2)

if __name__ == "__main__":
    input_dir = "/app/input"
    output_dir = "/app/output"
    with open("/app/input/input.json", "r") as f:
        data = json.load(f)
    persona = data.get("persona", "")
    job = data.get("job", "")

    analyzer = PersonaDrivenAnalyzer()
    analyzer.run(input_dir, output_dir, persona, job)
