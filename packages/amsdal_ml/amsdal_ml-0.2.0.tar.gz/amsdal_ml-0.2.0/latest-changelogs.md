## [v0.2.0](https://pypi.org/project/amsdal_ml/0.2.0/) - 2025-12-16

### New Features

- Added `PythonTool`: Tool for executing Python functions within agents
- Added `FunctionalCallingAgent`: Agent specialized in functional calling with configurable tools
- Added `NLQueryRetriever`: Retriever for natural language queries on AMSDAL querysets
- Added `DefaultIngestionPipeline`: Pipeline for document ingestion including loader, cleaner, splitter, embedder, and store
- Added `ModelIngester`: High-level ingester for processing models with customizable pipelines and metadata
- Added `PdfLoader`: Document loader using pymupdf for PDF processing
- Added `TextCleaner`: Processor for cleaning and normalizing text
- Added `TokenSplitter`: Splitter for dividing text into chunks based on token count
- Added `OpenAIEmbedder`: Embedder for generating embeddings via OpenAI API
- Added `EmbeddingDataStore`: Store for saving embedding data linked to source objects