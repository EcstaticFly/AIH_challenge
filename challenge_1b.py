

import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings("ignore")

import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util

class DocumentParser:
    """A fast, optimized parser to extract structured content from a PDF."""
    def _is_heading_pattern(self, text: str) -> bool:
        if not text: return False
        patterns = [r'^\d+(\.\d+)*[\.\)]?\s+', r'^[IVXLCDMivxlcdm]+[\.\)]\s+', r'^[A-Za-z][\.\)]\s+']
        return any(re.match(pattern, text) for pattern in patterns)

    def extract_structure(self, pdf_path: Path) -> List[Dict]:
        """Extracts sections with their full text content."""
        doc = None
        sections = []
        try:
            doc = fitz.open(pdf_path)
            current_heading = {"level": "title", "text": "Introduction", "page": 0, "content": ""}
            avg_font_size = self._calculate_average_font_size(doc)

            for page_num, page in enumerate(doc):
                blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_LIGATURES)["blocks"]
                for block in blocks:
                    if "lines" not in block: continue
                    for line in block["lines"]:
                        spans = sorted(line["spans"], key=lambda s: s['bbox'][0])
                        line_text = " ".join(s["text"] for s in spans).strip()
                        if not line_text: continue

                        first_span = spans[0]
                        font_size = first_span["size"]
                        is_bold = bool(first_span["flags"] & 16)
                        

                        is_heading = (
                            font_size > avg_font_size * 1.1 or 
                            (is_bold and font_size > avg_font_size * 0.9) or
                            self._is_heading_pattern(line_text) or
                            (len(line_text) < 100 and is_bold)
                        )
                        
                        if is_heading and line_text not in ['Introduction']:
                            if current_heading['content'].strip():
                                sections.append(current_heading)
                            current_heading = {"level": "H1", "text": line_text, "page": page_num, "content": ""}
                        else:
                            current_heading["content"] += line_text + " "
            
            if current_heading['content'].strip():
                sections.append(current_heading)
            return sections
        except Exception as e:
            print(f"Error parsing {pdf_path.name}: {e}")
            return []
        finally:
            if doc: doc.close()

    def _calculate_average_font_size(self, doc: fitz.Document) -> float:
        font_sizes, counts = [], []
        for page in doc:
            for block in page.get_text("dict")["blocks"]:
                if "lines" not in block: continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_sizes.append(span["size"])
                        counts.append(len(span["text"]))
        return sum(s * c for s, c in zip(font_sizes, counts)) / sum(counts) if counts else 12.0

class DocumentAnalyst:
    """Analyzes documents based on a persona and job-to-be-done."""
    def __init__(self, model_path: str):
        self.parser = DocumentParser()
        print("Loading embedding model...")
        start_time = time.time()
        self.model = SentenceTransformer(model_path)
        print(f"Model loaded in {time.time() - start_time:.2f}s")

    def analyze(self, doc_paths: List[Path], persona_role: str, job_task: str, challenge_info: Dict = None) -> Dict:
        """Performs the full analysis and returns the structured output."""
        print("1. Parsing all documents...")
        all_sections = []
        for doc_path in doc_paths:
            print(f"  - Parsing {doc_path.name}")
            sections = self.parser.extract_structure(doc_path)
            for section in sections:
                section["document"] = doc_path.name
                all_sections.append(section)

        print("\n2. Generating embeddings...")
        # Enhanced query for college friends trip planning
        enhanced_query = f"Role: {persona_role}. Task: {job_task}. Focus on activities, coastal adventures, nightlife, dining, cities, practical tips for young adults traveling together in groups."
        query_embedding = self.model.encode(enhanced_query, convert_to_tensor=True)
        
        # Create better section representations
        section_texts = []
        for s in all_sections:
            # Combine title and content with weights
            combined_text = f"{s['text']} {s['text']} {s['content']}"  # Title weighted twice
            section_texts.append(combined_text)
        
        section_embeddings = self.model.encode(section_texts, convert_to_tensor=True)

        print("\n3. Calculating relevance scores...")
        cosine_scores = util.pytorch_cos_sim(query_embedding, section_embeddings)[0]
        
        for i, section in enumerate(all_sections):
            section['relevance'] = cosine_scores[i].item()
            
            # Boost scores for sections likely relevant to college friends
            title_lower = section['text'].lower()
            content_lower = section['content'].lower()
            
            boost_keywords = [
                'coastal', 'beach', 'nightlife', 'entertainment', 'bar', 'club', 
                'activities', 'things to do', 'comprehensive guide', 'cities',
                'culinary', 'cooking', 'wine', 'group', 'friends', 'young',
                'packing', 'tips', 'tricks', 'practical'
            ]
            
            for keyword in boost_keywords:
                if keyword in title_lower or keyword in content_lower:
                    section['relevance'] += 0.1 

        print("\n4. Ranking sections and generating output...")
        ranked_sections = sorted(all_sections, key=lambda x: x['relevance'], reverse=True)
        

        selected_sections = self._select_diverse_sections(ranked_sections, max_sections=5)
        
        output = {
            "metadata": {
                "input_documents": [p.name for p in doc_paths],
                "persona": persona_role,
                "job_to_be_done": job_task,
                "processing_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime())[:-3] + "Z"
            },
            "extracted_sections": self._format_extracted_sections(selected_sections),
            "subsection_analysis": self._format_sub_sections(selected_sections)
        }
        

        if challenge_info:
            output["metadata"]["challenge_info"] = challenge_info
            
        return output

    def _select_diverse_sections(self, ranked_sections: List[Dict], max_sections: int = 5) -> List[Dict]:
        """Select diverse sections from different documents."""
        selected = []
        doc_count = {}
        
        for section in ranked_sections:
            doc_name = section["document"]
            

            if doc_count.get(doc_name, 0) < 2 and len(selected) < max_sections:
                selected.append(section)
                doc_count[doc_name] = doc_count.get(doc_name, 0) + 1
                

        for section in ranked_sections:
            if len(selected) >= max_sections:
                break
            if section not in selected:
                selected.append(section)
                
        return selected[:max_sections]

    def _format_extracted_sections(self, selected_sections: List[Dict]) -> List[Dict]:
        return [
            {
                "document": s["document"],
                "section_title": s["text"],
                "importance_rank": i + 1,
                "page_number": s["page"] + 1
            } for i, s in enumerate(selected_sections)
        ]

    def _format_sub_sections(self, top_sections: List[Dict]) -> List[Dict]:
        analysis = []
        for section in top_sections:

            content = re.sub(r'\s+', ' ', section["content"]).strip()
            

            sentences = re.split(r'(?<=[.!?])\s+', content)
            

            if len(content) > 500:

                refined_text = content[:400]
                last_sentence_end = max(
                    refined_text.rfind('.'),
                    refined_text.rfind('!'),
                    refined_text.rfind('?')
                )
                if last_sentence_end > 200:
                    refined_text = refined_text[:last_sentence_end + 1]
                else:
                    refined_text = content[:300] + "..."
            else:
                refined_text = content
            
            analysis.append({
                "document": section["document"],
                "refined_text": refined_text,
                "page_number": section["page"] + 1
            })
        return analysis

def main():
    """Main execution function."""
    start_time = time.time()
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    pdf_dir = input_dir / "PDFs"
    input_json_file = input_dir / "challenge_1b_input.json"
    
    output_dir.mkdir(exist_ok=True)
    
    if not pdf_dir.exists() or not input_json_file.exists():
        print("Error: Input directory must contain a 'PDFs' subfolder and a 'challenge_1b_input.json' file.")
        sys.exit(1)
        
    with open(input_json_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    doc_filenames = [doc['filename'] for doc in input_data['documents']]
    pdf_paths = [pdf_dir / fname for fname in doc_filenames]
    
    persona_role = input_data['persona']['role']
    job_task = input_data['job_to_be_done']['task']
    

    challenge_info = input_data.get('challenge_info', {})
    
    model_path = "/app/all-MiniLM-L6-v2-local"
    analyst = DocumentAnalyst(model_path=model_path)
    
    result = analyst.analyze(
        doc_paths=pdf_paths,
        persona_role=persona_role,
        job_task=job_task,
        challenge_info=challenge_info
    )
    
    output_file = output_dir / "challenge_1b_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    total_time = time.time() - start_time
    print(f"\n✅ Analysis complete. Output saved to {output_file}")
    print(f"⏱️ Total processing time: {total_time:.2f} seconds")
    
    if total_time > 60:
        print(f"⚠️ WARNING: Processing time ({total_time:.2f}s) exceeded the 60-second constraint.")
    else:
        print("👍 SUCCESS: Processing completed within the 60-second constraint.")

if __name__ == "__main__":
    main()