# Word-Level Plagiarism Checker

### A DSA-Based Document Similarity Analysis System

## About the Project

The **Word-Level Plagiarism Checker** is a Python-based project designed to identify similar words and phrases across multiple documents and research papers.

Manually comparing lengthy documents can be time-consuming. This project aims to simplify the process by automatically comparing text, calculating similarity scores, and identifying potential sources of matching content.

It demonstrates how Data Structures and Algorithms (DSA) can solve real-world problems in text processing and document analysis.

## Features

- **Multiple Document Comparison:** Compare several documents to identify overlapping content.
- **Research Paper Checking:** Compare documents against a collection of reference papers.
- **Word and Phrase Matching:** Identify matching text using string-searching algorithms.
- **Similarity Scores:** Measure textual overlap using similarity metrics.
- **Source Identification:** Find and rank documents containing similar content.
- **Match Highlighting:** Help users locate matching words and phrases.
- **Interactive Interface:** Present results in an organized and easy-to-understand format.

## DSA Concepts Used

| Algorithm / Concept | Purpose |
|---|---|
| KMP Algorithm | Find patterns efficiently in text |
| Rabin–Karp Algorithm | Search for patterns using hashing |
| Z Algorithm | Identify pattern occurrences |
| HashMap and HashSet | Store and retrieve text efficiently |
| Inverted Index | Find documents containing specific words |
| Jaccard Similarity | Measure overlap between sets of words |
| TF-IDF and Cosine Similarity | Compare document similarity |
| Dynamic Programming (LCS) | Identify common sequences of text |

*The final list should include only the algorithms implemented in the project.*

## How It Works

1. **Upload:** Select the documents to compare.
2. **Extract:** Read the text from supported file formats.
3. **Process:** Clean and divide the text into words and phrases.
4. **Compare:** Search for matching content using the implemented algorithms.
5. **Analyze:** Calculate similarity scores and identify potential sources.
6. **Review:** Display matching passages and comparison results.

## Technology Stack

- **Language:** Python
- **Interface:** Streamlit
- **Document Processing:** PDF, DOCX, and TXT parsing libraries
- **Similarity Analysis:** Custom algorithms and relevant Python libraries
- **Development Tools:** Visual Studio Code, Git, and GitHub

## Installation and Setup

**1. Clone the repository**

```bash
git clone <your-repository-url>
cd word-level-plagiarism-checker
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
```

On Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

**3. Install the dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the application**

```bash
streamlit run main.py
```

Open the local URL displayed in the terminal to use the application.

*These commands assume your project uses Streamlit, `main.py`, and a `requirements.txt` file.*

## Applications

- Academic assignment comparison
- Research paper similarity analysis
- Document verification
- Learning and demonstrating DSA concepts
- Searching collections of reference documents

## Future Scope

- Detect paraphrased content using semantic similarity techniques.
- Support additional file formats and languages.
- Improve performance when processing large document collections.
- Integrate authorized open-access research repositories.
- Enhance reports and source identification.

## Limitations

The results depend on the documents available for comparison. Exact matching algorithms may not detect paraphrased text, and similar content does not necessarily indicate plagiarism. Results should be reviewed alongside the original sources and citations.

## Authors

- **Saranya Aluru** — [GitHub](https://github.com/saranya-aluru)
- **DSriVarshini** — [GitHub](https://github.com/DSriVarshini)
- **Manya Akshitha** — [GitHub](https://github.com/manyaakshitha07)

**Project:** Word-Level Plagiarism Checker  
**Domain:** Data Structures and Algorithms (DSA)  
**Language:** Python

*Developed as an academic project demonstrating the practical application of Data Structures and Algorithms to document similarity analysis.*
