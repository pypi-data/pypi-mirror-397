# 🦜️🔗 LangChain Crawleo

[![PyPI version](https://badge.fury.io/py/langchain-crawleo.svg)](https://badge.fury.io/py/langchain-crawleo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This package contains the LangChain integration with [Crawleo](https://crawleo.dev/) - a privacy-first web search and crawler API.

## Features

- **CrawleoSearch**: Real-time web search with privacy-first approach
- **CrawleoCrawler**: Extract content from URLs with HTML/markdown support
- Full async support
- LangChain tool calling compatible

---

## Installation

```bash
pip install -U langchain-crawleo
```

### Credentials

Set your Crawleo API key as an environment variable:

you can get your API key from your [Crawleo dashboard](https://crawleo.dev/dashboard).

```python
import getpass
import os

if not os.environ.get("CRAWLEO_API_KEY"):
    os.environ["CRAWLEO_API_KEY"] = getpass.getpass("Crawleo API key:\n")
```

Or set it directly in your shell:

```bash
export CRAWLEO_API_KEY="your-api-key"
```

---

## Crawleo Search

The `CrawleoSearch` tool allows you to perform web searches using Crawleo's privacy-first Search API.

### Instantiation

The tool accepts various parameters during instantiation:

- `max_pages` (optional, int): Max result pages to crawl. Each page costs 1 credit. Default is 1.
- `setLang` (optional, str): Language code for search interface (e.g., "en", "es", "fr"). Default is "en".
- `cc` (optional, str): Country code for search results (e.g., "US", "GB", "DE").
- `geolocation` (optional, str): Geo location for search. Allowed: random, pl, gb, jp, de, fr, es, us. Default is "random".
- `device` (optional, str): Device simulation: "desktop", "mobile", or "tablet". Default is "desktop".
- `enhanced_html` (optional, bool): Return AI-enhanced, cleaned HTML. Default is True.
- `raw_html` (optional, bool): Return original, unprocessed HTML. Default is False.
- `page_text` (optional, bool): Return extracted plain text. Default is False.
- `markdown` (optional, bool): Return content in Markdown format. Default is True.

```python
from langchain_crawleo import CrawleoSearch

tool = CrawleoSearch(
    max_pages=1,
    cc="US",
    setLang="en",
    # geolocation="random",
    # device="desktop",
    # enhanced_html=True,
    # raw_html=False,
    # page_text=False,
    # markdown=True,
)
```

### Invoke directly with args

The Crawleo search tool accepts the following arguments during invocation:

- `query` (required): A natural language search query
- All other parameters can also be set during invocation

**NOTE**: If you set an argument during instantiation, you can override it during invocation.

```python
# Basic query
result = tool.invoke({"query": "What is Crawleo pricing?"})
print(result)
```

### Parameter Override Example

```python
# Instantiate with default country
search = CrawleoSearch(cc="US")

# Override country during invocation
result = search.invoke({"query": "local news", "cc": "DE"})
# This will use cc="DE" instead of "US"
```


### Full Example

```python
from langchain_crawleo import CrawleoSearch
search_tool = CrawleoSearch(
    max_pages=1,
    cc="US",
    setLang="en",
    markdown=True,
)
result = search_tool.invoke({"query": "What is the future of AI?"})
print(result)
```

### Response Format

The search API returns a JSON response with the following structure:

```json
{
  "status": "success",
  "data": {
    "query": "What is the future of AI?",
    "pages_fetched": 1,
    "time_used": 1.51,
    "pages": {
      "1": {
        "total_results": "About 523,000 results",
        "search_results": [
          {
            "title": "The Future of AI: Trends and Predictions",
            "link": "https://example.com/ai-future",
            "date": "Mar 12, 2024",
            "snippet": "Artificial Intelligence is rapidly evolving...",
            "domain": "example.com"
          }
        ],
        "page_content": {
          "page_ai_enhanced_html": "...",
          "page_text_markdown": "..."
        }
      }
    },
    "credits_used": 1
  }
}
```

---

## Crawleo Crawler

The `CrawleoCrawler` tool allows you to extract content from specific URLs using Crawleo's Crawler API.

### Instantiation

The tool accepts various parameters during instantiation:

- `raw_html` (optional, bool): Whether to return raw HTML content. Default is False.
- `markdown` (optional, bool): Whether to return content in markdown format. Default is False.

```python
from langchain_crawleo import CrawleoCrawler

tool = CrawleoCrawler(
    markdown=True,
    # raw_html=False,
)
```

### Invoke directly with args

The Crawleo crawler tool accepts the following arguments during invocation:

- `urls` (required): A list of URLs to crawl (1-20 URLs)
- `raw_html` (optional): Override raw_html setting
- `markdown` (optional): Override markdown setting

```python
# Crawl a single URL
result = tool.invoke({"urls": ["https://crawleo.dev"]})
print(result)

# Crawl multiple URLs
result = tool.invoke({
    "urls": [
        "https://example.com",
        "https://another-site.com"
    ]
})
```

---

## Agent Tool Calling

You can use Crawleo tools directly with a LangChain agent. This allows the agent to dynamically set arguments.

```python
import datetime
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage
from langchain_crawleo import CrawleoSearch, CrawleoCrawler

# Initialize LLM
llm = init_chat_model(model="gpt-4o", model_provider="openai", temperature=0)

# Initialize Crawleo Tools
search_tool = CrawleoSearch(max_pages=1)
crawler_tool = CrawleoCrawler(markdown=True)

# Set up Prompt
today = datetime.datetime.today().strftime("%D")
prompt = ChatPromptTemplate.from_messages([
    ("system", f"""You are a helpful research assistant. You can search the web 
    and crawl specific URLs for information. The date today is {today}."""),
    MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create an agent that can use tools
tools = [search_tool, crawler_tool]
agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)

# Create an Agent Executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run the agent
user_input = "Search for Crawleo features and then crawl their homepage"
response = agent_executor.invoke({"messages": [HumanMessage(content=user_input)]})
print(response)
```

---

## Async Support

Both tools support async operations:

```python
import asyncio
from langchain_crawleo import CrawleoSearch, CrawleoCrawler

async def main():
    # Async search
    search = CrawleoSearch(max_pages=1)
    search_result = await search.ainvoke({"query": "Crawleo features"})
    print(search_result)
    
    # Async crawl
    crawler = CrawleoCrawler(markdown=True)
    crawl_result = await crawler.ainvoke({"urls": ["https://crawleo.dev"]})
    print(crawl_result)

asyncio.run(main())
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CRAWLEO_API_KEY` | Your Crawleo API key (required) | - |
| `CRAWLEO_BASE_URL` | Custom API base URL (optional) | `https://api.crawleo.dev/api/v1` |

---

## Error Handling

The tools provide helpful error messages and suggestions when things go wrong:

```python
from langchain_crawleo import CrawleoSearch

search = CrawleoSearch()

try:
    result = search.invoke({"query": "very obscure query with no results"})
except Exception as e:
    print(f"Error: {e}")
    # Error will include suggestions like:
    # "Try increasing max_pages for more results"
    # "Try a different or more specific query"
```

### Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid or missing parameters |
| 401 | Unauthorized - Invalid or missing API key |
| 429 | Too Many Requests - Rate limit or quota exceeded |
| 500 | Internal Server Error - Something went wrong on the server |

---

## Real-World Usage Examples

### Example 1: Summarize Search Results with an LLM

Use CrawleoSearch to fetch results, then pass them to a model for summarization.

```python
import os
from langchain_crawleo import CrawleoSearch
from langchain_openai import ChatOpenAI

os.environ["CRAWLEO_API_KEY"] = "YOUR_API_KEY"
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

# Initialize search tool
search = CrawleoSearch(max_pages=1, setLang="en", cc="US", markdown=True)

# Fetch search results
raw = search.invoke({"query": "Crawleo vs other web scraping APIs"})

# Extract snippets from results
page = raw["data"]["pages"]["1"]
snippets = [
    f"- {item['title']}: {item['snippet']}"
    for item in page["search_results"]
    if item.get("snippet")
]
context = "\n".join(snippets)

# Summarize with LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
summary = llm.invoke(
    f"""You are a technical analyst. Here are search results about web scraping APIs:

{context}

Write a short, objective comparison of the options mentioned."""
)

print(summary.content)
```

---

### Example 2: Current Events QA with LangChain Agent

Let an agent decide when to call CrawleoSearch to answer time-sensitive questions.

```python
import os
from langchain_crawleo import CrawleoSearch
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

os.environ["CRAWLEO_API_KEY"] = "YOUR_API_KEY"
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

search_tool = CrawleoSearch(max_pages=1, setLang="en", markdown=True)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a web research assistant. Use the Crawleo search tool "
               "for current information and cite sources when possible."),
    MessagesPlaceholder("messages"),
    MessagesPlaceholder("agent_scratchpad"),
])

agent = create_tool_calling_agent(llm=llm, tools=[search_tool], prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=[search_tool], verbose=True)

response = agent_executor.invoke({
    "messages": [("user", "What are the latest AI regulations in the EU?")]
})

print(response["output"])
```

---

### Example 3: Geo-Targeted News Search

Control `cc` and `geolocation` to tailor results to a specific region.

```python
import os
from langchain_crawleo import CrawleoSearch

os.environ["CRAWLEO_API_KEY"] = "YOUR_API_KEY"

# Search for German news
search = CrawleoSearch(
    max_pages=1,
    setLang="de",      # German language interface
    cc="DE",           # Country code for Germany
    geolocation="de",  # Geo-localized search
)

result = search.invoke({"query": "KI Regulierung Neuigkeiten"})  # "AI regulation news" in German

for item in result["data"]["pages"]["1"]["search_results"][:5]:
    print(f"{item.get('date', 'N/A')} | {item['title']}")
    print(f"  → {item['link']}\n")
```

---

### Example 4: Compare Desktop vs Mobile Search Results

Different devices can return different SERPs. Use `device` to compare.

```python
import os
from langchain_crawleo import CrawleoSearch

os.environ["CRAWLEO_API_KEY"] = "YOUR_API_KEY"

query = "best restaurants near me"

desktop_search = CrawleoSearch(device="desktop", max_pages=1)
mobile_search = CrawleoSearch(device="mobile", max_pages=1)

desktop_results = desktop_search.invoke({"query": query})
mobile_results = mobile_search.invoke({"query": query})

print("=== Desktop Results ===")
for item in desktop_results["data"]["pages"]["1"]["search_results"][:3]:
    print(f"- {item['title']}")

print("\n=== Mobile Results ===")
for item in mobile_results["data"]["pages"]["1"]["search_results"][:3]:
    print(f"- {item['title']}")
```

---

### Example 5: Async Concurrent Searches (Multi-Topic Dashboard)

Use `ainvoke` to run multiple searches in parallel for faster results.

```python
import asyncio
import os
from langchain_crawleo import CrawleoSearch

os.environ["CRAWLEO_API_KEY"] = "YOUR_API_KEY"

async def main():
    topics = [
        "artificial intelligence trends 2025",
        "climate change solutions",
        "remote work best practices",
    ]

    tool = CrawleoSearch(max_pages=1, setLang="en", markdown=True)

    # Run all searches concurrently
    tasks = [tool.ainvoke({"query": topic}) for topic in topics]
    results = await asyncio.gather(*tasks)

    for topic, result in zip(topics, results):
        print(f"\n{'='*50}")
        print(f"Topic: {topic}")
        print(f"{'='*50}")
        page = result["data"]["pages"]["1"]
        for item in page["search_results"][:3]:
            print(f"  • {item['title']}")
            print(f"    {item.get('snippet', '')[:100]}...")

asyncio.run(main())
```

---

### Example 6: Search-Then-Answer RAG Pattern

Use Crawleo as a real-time retriever for retrieval-augmented generation without indexing.

```python
import os
from langchain_crawleo import CrawleoSearch
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

os.environ["CRAWLEO_API_KEY"] = "YOUR_API_KEY"
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

search = CrawleoSearch(max_pages=1, markdown=True)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

user_question = "How does Crawleo handle JavaScript-heavy websites?"

# Step 1: Search for relevant information
search_result = search.invoke({"query": user_question})
page = search_result["data"]["pages"]["1"]

# Step 2: Build context from search results
snippets = []
for item in page["search_results"][:5]:
    snippet = item.get("snippet", "")
    link = item.get("link", "")
    snippets.append(f"- {item['title']} ({link}): {snippet}")
context = "\n".join(snippets)

# Step 3: Generate answer using LLM
prompt = ChatPromptTemplate.from_template(
    """You are a technical documentation assistant.

Use the search results below to answer the user's question.
If information is unclear, say so honestly.

Search results:
{context}

Question: {question}

Answer:"""
)

chain = prompt | llm
answer = chain.invoke({"context": context, "question": user_question})
print(answer.content)
```

---

### Example 7: Build a Simple CLI Search Tool

A quick command-line tool for searching from your terminal.

```python
#!/usr/bin/env python3
"""cli_search.py - Simple CLI search tool using Crawleo"""

import os
import sys
from langchain_crawleo import CrawleoSearch

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli_search.py <search query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    
    # Ensure API key is set
    if not os.environ.get("CRAWLEO_API_KEY"):
        print("Error: CRAWLEO_API_KEY environment variable not set")
        sys.exit(1)

    tool = CrawleoSearch(max_pages=1, setLang="en", markdown=True)
    result = tool.invoke({"query": query})

    if result.get("status") == "success":
        print(f"\n🔍 Search results for: {query}\n")
        print(f"Found {result['data']['pages']['1']['total_results']}\n")
        
        for i, item in enumerate(result["data"]["pages"]["1"]["search_results"][:10], 1):
            print(f"{i}. {item['title']}")
            print(f"   {item['link']}")
            if item.get("snippet"):
                print(f"   {item['snippet'][:150]}...")
            print()
    else:
        print(f"Error: {result}")

if __name__ == "__main__":
    main()
```

Run it:
```bash
export CRAWLEO_API_KEY="your-api-key"
python cli_search.py "Python web scraping tutorial"
```

---

### Example 8: Quick Integration Test

A minimal snippet to verify your setup is working correctly.

```python
# quick_test.py
import os
from langchain_crawleo import CrawleoSearch

os.environ["CRAWLEO_API_KEY"] = "YOUR_API_KEY"

tool = CrawleoSearch(max_pages=1, setLang="en", markdown=True)
result = tool.invoke({"query": "test search query"})

# Verify response
assert result.get("status") == "success", f"Unexpected status: {result}"
assert "data" in result, "Missing 'data' in response"
assert "pages" in result["data"], "Missing 'pages' in response"

first_result = result["data"]["pages"]["1"]["search_results"][0]
print("✅ Setup working!")
print(f"First result: {first_result['title']}")
print(f"Link: {first_result['link']}")
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

