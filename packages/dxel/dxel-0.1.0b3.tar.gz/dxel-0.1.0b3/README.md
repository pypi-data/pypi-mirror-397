
# dxel: AI-Powered Data Analysis Agent

dxel is an extensible Python package designed to automate and enhance data analysis workflows using Large Language Models (LLMs) and agent-based orchestration. It enables users to interact with their data, generate insights, and visualize results through natural language queries and intelligent agents.

## Project Overview

**Key Capabilities:**
- LLM-powered data analysis and summarization
- Automated data exploration and visualization
- Agent-based orchestration for complex workflows
- Extensible architecture for custom agents and LLMs
- Integration with multiple LLM providers (Gemini, Groq)

**Typical Use Cases:**
- Rapid data exploration and summary generation
- Automated report creation
- Interactive data querying and visualization
- Building custom data agents for business intelligence

**How It Works:**
1. Users provide a dataset and a natural language query.
2. dxel agents interpret the query, analyze the data, and return results or visualizations.
3. LLMs (like Gemini) are used for reasoning, summarization, and generating code or explanations.

The package is modular, allowing you to add new agents, LLM integrations, or utilities as needed.

**Note:**  
1. The current version supports multiple LLM providers: Gemini and Groq.
2. Set the appropriate API keys as environment variables: `GOOGLE_API_KEY` or `GROQ_API_KEY`.

## Prerequisites
- Python 3.11+
- Install dxel:
  ```
  pip install dxel
  ```
- Set your API key(s) as environment variables based on your chosen LLM provider:
  - For Gemini: `GOOGLE_API_KEY`
  - For Groq: `GROQ_API_KEY`



## Demo Notebook: Step-by-Step Walkthrough

### Using Gemini LLM

1. **Import Required Libraries and dxel Modules**
   - Import standard Python libraries (os, sys, pandas, numpy, etc.)
   - Import dxel modules:
     ```python
     from dxel.utils.llm.gemini import Gemini
     from dxel.datascience.agent import DataAnalystAgent
     ```

2. **Set Data Path and API Key**
   - Define the path to your dataset:
     ```python
     data_loc = 'notebook_io/data_agent/input/Titanic-Dataset.csv'
     ```
   - Load your Google Gemini API key from environment variables:
     ```python
     api_key = os.getenv('GOOGLE_API_KEY')
     ```

3. **Initialize Gemini LLM and DataAnalystAgent**
   - Create a Gemini LLM client:
     ```python
     gemini_llm = Gemini(api_key=api_key)
     ```
   - Initialize the DataAnalystAgent with the LLM and data:
     ```python
     data_analyst_agent = DataAnalystAgent(gemini_llm, data_loc)
     ```

4. **Run Data Analysis Queries**
   - Get column information:
     ```python
     data_analyst_agent.think('tell me all columns')
     ```

   - Get distribution of a column:
     ```python
     o = data_analyst_agent.think('give me distribution of age column')
     ```

### Using Groq LLM

Simply replace the Gemini initialization with Groq:

```python
from dxel.utils.llm.groq import GroqLLM

api_key = os.getenv('GROQ_API_KEY')
groq = GroqLLM(api_key=api_key, model="llama-3.3-70b-versatile")
data_analyst_agent = DataAnalystAgent(groq, data_loc)
```

Then run the same analysis queries as with Gemini.





## Features Demonstrated
- Multi-LLM support (Gemini, Groq)
- LLM-powered data analysis
- Data summarization and column insights
- Distribution queries and visualization

---
For more details, see the demo notebooks:
- [Gemini Demo](https://github.com/prashantgavit/DataGenie/blob/main/demo_notebook/data_analyst_agent_gemini.ipynb)
- [Groq Demo](https://github.com/prashantgavit/DataGenie/blob/main/demo_notebook/data_analyst_agent_groq.ipynb)
