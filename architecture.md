graph TD
subgraph "Phase 1: Knowledge Ingestion (One-time Setup)"
A1[Financial Books PDF] --> B(Ingest Script);
A2[Annual Reports PDF] --> B;
B --> C{Chunk Documents};
C --> D[Generate Embeddings <br> using OpenAI or Nomic];
D --> E[Store in Qdrant <br> Vector Database];
end

    subgraph "Phase 2: User Analysis Request"
        F[User runs CLI command <br> e.g., &quot;analyze company ITC&quot;] --> G{User Query};
    end

    subgraph "Phase 3: RAG & AI Analysis Pipeline"
        G --> H[1. Generate Embedding for Query];
        H --> I{2. Semantic Search <br> in Qdrant DB};
        I -- Retrieved Context --> J;
        E -- Stored Knowledge --> I;
        G -- Original Query --> J;
        J[3. Augment Prompt <br> &lpar;Query + Context&rpar;];
        J --> K{4. Send to LLM};
        K --> L{OpenAI API <br> Available?};
        L -- Yes --> M[Primary: <br> OpenAI GPT-4.1-nano];
        L -- No --> N[Fallback: <br> Local DeepSeek R1 via Ollama];
        M --> O[5. Perform Analysis <br> &lpar;Data Extraction, Ratios, Insights&rpar;];
        N --> O;
    end

    subgraph "Phase 4: Output"
        O --> P[Generate Comprehensive Report <br> &lpar;Metrics, Thesis, Recommendation&rpar;];
        P --> Q[Save Report in /reports folder];
    end

    style F fill:#cde4ff,stroke:#6699ff,stroke-width:2px
    style Q fill:#cde4ff,stroke:#6699ff,stroke-width:2px
