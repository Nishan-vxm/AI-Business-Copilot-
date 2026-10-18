# AI Business Copilot

A local-first analytics prototype that converts natural-language business questions into SQLite queries using **Qwen2.5-3B-Instruct**, executes read-only SQL against the Olist Brazilian ecommerce dataset, and displays results in a Gradio dashboard.

> **Status:** Educational / portfolio prototype. Not production-ready. SQL generation can be semantically incorrect even when a query executes successfully.

## Features

- Natural-language-to-SQL generation with Qwen2.5-3B-Instruct.
- SQLite-backed analytics over the Olist ecommerce dataset.
- Read-only database connection, SQLite authorizer, query-only mode, and basic SQL validation.
- Bounded retry when generated SQL fails.
- Gradio dashboard showing generated SQL, status, and query results.
- Basic safety-gate tests and manually verified benchmark examples.

## Architecture

```text
User question
    |
    v
Gradio UI (app.py)
    |
    v
Copilot orchestration (src/copilot.py)
    |                       |
    v                       v
Qwen SQL generation       SQL validation
(src/llm.py)                |
                            v
                  Read-only SQLite execution
                    (src/database.py)
                            |
                            v
                      Result dataframe
                            |
                            v
                     Gradio UI response
```

## Requirements

- Python 3.10 or 3.11 recommended.
- A machine with enough RAM for the model; a CUDA GPU is recommended.
- Internet access on first run to download the model and dataset.
- The Qwen2.5-3B-Instruct model is downloaded through Hugging Face Transformers at runtime.
- Dataset access is handled by KaggleHub. Review the dataset's terms and access requirements.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-business-copilot.git
cd ai-business-copilot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

### 3. Install dependencies

Install a PyTorch build suitable for your operating system and hardware from the official PyTorch installation selector if the default install does not fit your environment, then:

```bash
pip install -r requirements.txt
```

### 4. Download the dataset and build SQLite

```bash
python scripts/setup_data.py
```

This creates `data/olist_business.db`. The `data/` directory is ignored by Git and should not be committed.

### 5. Start the app

```bash
python app.py
```

Open `http://127.0.0.1:7860`.

On first run, the model weights may take time to download. On a limited-RAM machine, use Google Colab with a GPU runtime.

## Google Colab

1. Upload or clone this repository in a Colab notebook.
2. Install dependencies.
3. Run `python scripts/setup_data.py`.
4. Run `python app.py`.

Colab sessions are temporary. The downloaded model and database may need to be recreated after a runtime reset.

## Example questions

- How many orders are there in the database?
- How many orders were delivered?
- What is the average payment value?
- Show the 5 states with the most customers.
- How many orders were placed in 2018?

## Evaluation notes

During development, these values were independently checked against the same local dataset using direct SQL and Pandas:

| Check | Verified value |
|---|---:|
| Total orders | 99,441 |
| Unique customer IDs | 96,096 |
| Delivered orders | 96,478 |
| Orders purchased in 2018 | 54,011 |

These checks validate those fixed queries only. They **do not** establish overall LLM accuracy. Manual stress tests found examples where SQL executed but answered the wrong question, such as querying sellers when asked for customers by state. Semantic evaluation and broader tests remain future work.

## Safety and limitations

- This project is a prototype, not a secure multi-user analytics service.
- The SQL validator is regex-based and is not a full SQL parser.
- Read-only SQLite mode and an authorizer provide defense-in-depth, but do not replace a hardened sandbox.
- `max_rows` caps returned rows; it does not guarantee that query execution is cheap.
- Query timeout handling is approximate.
- A syntactically valid query may still be logically wrong or misleading.
- Do not expose this app publicly with sensitive or private data.
- The default app launches locally with `share=False`. Do not enable public sharing without reviewing access controls.

## Tests

Run the lightweight SQL validation tests:

```bash
pytest -q
```

These tests do not load the model or require a GPU.

## Project structure

```text
ai-business-copilot/
├── app.py
├── src/
│   ├── __init__.py
│   ├── copilot.py
│   ├── database.py
│   └── llm.py
├── scripts/
│   └── setup_data.py
├── tests/
│   └── test_queries.py
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Roadmap

- [ ] Expand semantic correctness benchmark with expected outputs.
- [ ] Add schema-aware checks and better retry prompts.
- [ ] Add query logging with sensitive-data safeguards.
- [ ] Add charts for supported result types.
- [ ] Separate frontend and API for deployment.
- [ ] Add authentication and stronger resource controls before any multi-user deployment.

## Acknowledgements

- Olist Brazilian ecommerce public dataset, accessed through KaggleHub.
- Qwen2.5 Instruct model family by Qwen.
- Gradio, Hugging Face Transformers, PyTorch, pandas, and SQLite.
