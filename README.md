# Challenge 1B: Persona-Driven Document Intelligence

## Overview

This solution implements an intelligent document analyst that extracts and prioritizes the most relevant sections from a collection of documents based on a specific persona and their job-to-be-done. The system uses semantic similarity analysis to identify and rank content that best matches the user's requirements.

## Challenge Theme

**"Connect What Matters — For the User Who Matters"**

## Solution Architecture

### Core Components

1. **DocumentParser**: Extracts structured content from PDFs using PyMuPDF

   - Identifies headings and sections using font analysis
   - Maintains document structure and page references
   - Handles various document formats and layouts

2. **DocumentAnalyst**: Analyzes documents using semantic embeddings
   - Uses SentenceTransformer (all-MiniLM-L6-v2) for text embeddings
   - Calculates cosine similarity between query and sections
   - Implements relevance boosting for domain-specific keywords
   - Ensures diverse section selection across documents

### Key Features

- **Generic Solution**: Handles diverse domains (research papers, financial reports, textbooks, etc.)
- **Persona-Aware**: Adapts analysis based on user role and expertise
- **Task-Oriented**: Prioritizes content relevant to specific job-to-be-done
- **Fast Processing**: Optimized for 60-second constraint
- **CPU-Only**: No GPU requirements
- **Offline**: No internet access needed during execution

## Technical Specifications

- **Model**: all-MiniLM-L6-v2 (sentence-transformers)
- **Model Size**: ~90MB (well under 1GB limit)
- **Processing Time**: <60 seconds for 3-5 documents
- **Architecture**: CPU-only execution
- **Dependencies**: PyMuPDF, sentence-transformers, numpy

## Input/Output Format

### Input Structure

```
/app/input/
├── PDFs/
│   ├── document1.pdf
│   ├── document2.pdf
│   └── ...
└── challenge_1b_input.json
```

### Input JSON Format

```json
{
  "challenge_info": {
    "challenge_id": "round_1b_002",
    "test_case_name": "xyz",
    "description": "xyz"
  },
  "documents": [
    { "filename": "document1.pdf" },
    { "filename": "document2.pdf" }
  ],
  "persona": {
    "role": "PhD Researcher in Computational Biology"
  },
  "job_to_be_done": {
    "task": "Prepare a comprehensive literature review"
  }
}
```

### Output JSON Format

```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "PhD Researcher",
    "job_to_be_done": "Literature review",
    "processing_timestamp": "2025-07-28T17:12:31.632389Z"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "section_title": "Methodology",
      "importance_rank": 1,
      "page_number": 3
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "refined_text": "Detailed analysis...",
      "page_number": 3
    }
  ]
}
```

## Installation & Usage

### Prerequisites

- Docker Desktop installed
- At least 4GB RAM available
- PDF documents and input JSON file ready

### Build the Docker Image

```bash
docker build -t challenge1b-solution:latest .
```

### Run the Solution

```bash
# Windows PowerShell
docker run --rm -v "${PWD}/input:/app/input" -v "${PWD}/output:/app/output" --network none challenge1b-solution:latest

# Linux/Mac
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none challenge1b-solution:latest

# Git Bash (Windows)
MSYS_NO_PATHCONV=1 docker run --rm -v "${PWD}/input:/app/input" -v "${PWD}/output:/app/output" --network none challenge1b-solution:latest
```

### Expected Output

- Processing logs showing progress
- Final JSON output saved to `/app/output/challenge_1b_output.json`
- Performance metrics (processing time)

## Performance Characteristics

- **Processing Speed**: 20-45 seconds for 5-7 documents
- **Memory Usage**: ~2GB RAM during processing
- **Accuracy**: High relevance scoring with semantic understanding
- **Scalability**: Handles 3-10 documents efficiently

## Error Handling

The system includes robust error handling for:

- Missing input files or directories
- Corrupted PDF documents
- Memory constraints
- Invalid JSON format
- Processing timeouts

## Constraints Compliance

✅ **CPU-only execution** - No GPU dependencies  
✅ **Model size ≤ 1GB** - Uses 90MB sentence transformer  
✅ **Processing time ≤ 60s** - Optimized for speed  
✅ **No internet access** - Fully offline operation  
✅ **Generic solution** - Handles diverse domains and personas

## Troubleshooting

### Common Issues

1. **"Input directory must contain..."**

   - Ensure `PDFs` folder and `challenge_1b_input.json` exist in input directory
   - Check file permissions and paths

2. **Docker path issues (Windows)**

   - Use PowerShell instead of Git Bash
   - Or use `MSYS_NO_PATHCONV=1` prefix in Git Bash

3. **Out of memory errors**

   - Reduce number of documents
   - Increase Docker memory allocation

4. **Slow processing**
   - Check document sizes (very large PDFs may exceed time limit)
   - Ensure sufficient system resources

### Performance Tips

- Use documents with clear structure and headings
- Provide specific, detailed persona descriptions
- Keep job-to-be-done tasks concrete and actionable
- Ensure adequate system memory (4GB+ recommended)

## Development Notes

- Built with Python 3.9
- Uses slim Docker base image for efficiency
- Implements caching for model loading
- Includes comprehensive logging for debugging

## License

This solution is developed for the Adobe Hackathon Challenge 1B and follows the competition guidelines and constraints.
