# Multi-Agent Research System

An AI-powered research system that uses multiple agents to search the web, extract detailed information, generate research reports, and review the final output.

## Features

- **Search Agent** — Finds relevant information using Tavily Search.
- **Reader Agent** — Scrapes relevant webpages using BeautifulSoup.
- **Writer Chain** — Generates a structured research report using LCEL.
- **Critic Chain** — Reviews the report and provides feedback.
- **Streamlit UI** — A clean, modern interface for running research and viewing results.

## Workflow

1. Enter a research topic.
2. The Search Agent gathers relevant information.
3. The Reader Agent scrapes a relevant webpage.
4. The Writer Chain generates a research report.
5. The Critic Chain reviews the report.
6. View the results in the Streamlit interface.

## Project Structure

```text
research_agent/
├── agents.py
├── main.py
├── pipeline.py
├── tools.py
├── README.md
├── requirements.txt
├── pyproject.toml
└── uv.lock
```

## Setup

Clone the repository and navigate to the project directory.

Install dependencies using `uv`:

```bash
uv sync
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## Run the Application

Run the research pipeline:

```bash
uv run python pipeline.py
```

Run the Streamlit interface (once implemented):

```bash
uv run streamlit run main.py
```

## Tech Stack

- Python
- LangChain
- LCEL (LangChain Expression Language)
- Groq API
- Tavily Search API
- BeautifulSoup
- Streamlit

## Future Improvements

- Multi-source research and source citations
- Improved report quality and evaluation
- Research history and report export
