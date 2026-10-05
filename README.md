# CloudDesk AI Support Engineer

CloudDesk is an AI-powered technical support assistant built using **Retrieval-Augmented Generation (RAG)**. The application retrieves relevant information from a CloudDesk knowledge base before using a language model to generate a response.

The aim of the project is to provide support engineers with faster access to relevant troubleshooting information while reducing unsupported or inaccurate responses.

## Project Overview

The system works by taking a user's support question, finding relevant information from the knowledge base, and passing that information to a language model as context.

The main workflow is:

```text
User Question
      ↓
Query Embedding
      ↓
Semantic Search
      ↓
Relevant Documents
      ↓
Confidence Check
      ↓
LLM Response / Escalation
```

The knowledge base currently contains information from:

* Engineering runbooks
* Support tickets
* Help centre articles
* Release notes
* API documentation

The current dataset has **105 processed chunks** with metadata such as source type, document title, version, last updated date, source file and chunk ID.

## Tech Stack

* **Python**
* **Sentence Transformers**
* **all-MiniLM-L6-v2**
* **Pinecone**
* **ChromaDB**
* **FAISS**
* **Hugging Face**
* **Streamlit**
* **Jupyter Notebook**
* **Git/GitHub**

## Data Processing

The project includes an ingestion pipeline for PDF, Markdown and CSV files.

The pipeline:

1. Loads the source files
2. Extracts and standardises the content
3. Splits the content into smaller chunks
4. Adds metadata to each chunk
5. Generates embeddings
6. Stores the vectors for semantic retrieval

The embedding model used is `all-MiniLM-L6-v2`, which produces **384-dimensional embeddings**.

## Retrieval

Pinecone is used as the main vector database for storing and searching the embeddings.

ChromaDB and FAISS are also included to support local vector search during development and testing.

For each question, the retrieval pipeline searches for the most relevant chunks from the knowledge base. The retrieved documents are then used as context for the language model.

Retrieved results include their source information and similarity scores, which helps with traceability and evaluation.

## LLM Integration

The project uses the Hugging Face inference API to generate responses based on the retrieved context.

The model is instructed to:

* Use the provided context when answering
* Avoid making unsupported claims
* Give clear troubleshooting steps
* Refer to the relevant sources
* State when the available information is not sufficient
* Escalate questions when confidence is too low

## Confidence and Escalation

A confidence score is calculated using the similarity scores from the retrieved documents.

The current baseline threshold is **60%**.

Questions below this threshold are flagged for escalation rather than being treated as sufficiently supported by the available knowledge.

The confidence score is currently a retrieval-based heuristic and is not intended to represent a calibrated probability of correctness.

## Evaluation

A separate retrieval and evaluation pipeline was developed using historical support questions.

The evaluation looks at:

* Retrieved documents
* Similarity scores
* Source matching
* Hit@K retrieval performance
* Confidence scores
* Escalation decisions

Further testing and optimisation are being carried out as part of the project.

## Streamlit Interface

A simple Streamlit chat interface was developed to interact with the support assistant.

Example questions:

```text
How do I integrate Slack with CloudDesk?

My SAML login stopped working after adding a new domain.

Why are webhook deliveries failing?
```

The application returns the generated response along with confidence and supporting source information.

## Project Structure

```text
CloudDesk-Ai-Support-Engineer/
│
├── app.py
├── streamlit_app .py
├── retrieval_pipeline.py
├── requirements.txt
├── context_str_view.html
│
├── 01_data_ingestion_and_indexing.ipynb
├── 02_retrieval_and_evaluation_pipeline.ipynb
│
├── data/
│   ├── engineering_runbooks/
│   ├── support_tickets/
│   ├── release_notes/
│   ├── help_center_articles/
│   └── api_documentation/
│
└── vector_db/
    └── chunks_store.json
```

## Documentation

For detailed guides and references, see the `docs/` folder:

* **[QUICKSTART.md](docs/QUICKSTART.md)** - Getting started guide
* **[DEPLOY_STREAMLIT_CLOUD.md](docs/DEPLOY_STREAMLIT_CLOUD.md)** - Cloud deployment instructions
* **[SYSTEM_SUMMARY.txt](docs/SYSTEM_SUMMARY.txt)** - Complete system architecture
* **[ONE_PAGE_SUMMARY.txt](docs/ONE_PAGE_SUMMARY.txt)** - Quick 2-minute overview
* **[ARCHITECTURE_EXPLAINED.md](docs/ARCHITECTURE_EXPLAINED.md)** - Detailed architecture with diagrams
* **[README_REFERENCE_GUIDE.md](docs/README_REFERENCE_GUIDE.md)** - Master index of all documentation
* **[FRONTEND_BACKEND_CLARIFICATION.md](docs/FRONTEND_BACKEND_CLARIFICATION.md)** - Frontend/backend explanation

## Project Goals

The main goals of the project are to:

* Improve access to technical support information
* Ground AI responses in approved documentation
* Provide source traceability
* Identify low-confidence questions
* Reduce unsupported troubleshooting instructions
* Provide a clear route for human escalation

## Disclaimer

This project is a prototype for demonstrating an AI-assisted technical support workflow. Responses should be checked against approved documentation and support procedures before being used in a production environment.
