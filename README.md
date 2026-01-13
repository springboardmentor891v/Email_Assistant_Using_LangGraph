# Email_Assistant_Using_LangGraph

The primary objective of this project is to design, build, and deploy a next-generation, autonomous email assistant using LangGraph. This project moves beyond a simple reactive agent. The goal is to create a sophisticated, "ambient" agent that proactively manages email workflows.

## Project Structure

- **main.ipynb** - Main project notebook with LangGraph implementation
- **notebook/gemini_api.ipynb** - Gemini API integration and configuration notebook
- **ProjectObejective.md** - Detailed project objectives and goals

## Setup Instructions

### Prerequisites
- Python 3.8+
- GEMINI_API_KEY environment variable set

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Email_Assistant_Using_LangGraph
```

2. Install required dependencies:
```bash
pip install langchain-google-genai langchain-core langgraph pydantic google-generativeai python-dotenv
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
GEMINI_API_KEY=your_api_key_here
```

## Technologies Used

- **LangGraph** - For building stateful, multi-actor applications
- **LangChain** - For LLM integration and tools
- **Google Generative AI** - Gemini API for language model capabilities
- **Python** - Core programming language
- **Pydantic** - Data validation using Python type annotations

## Key Features

- Integration with Google's Gemini API
- Tool-based agent architecture using LangGraph
- Memory persistence with MemorySaver
- Type-safe workflow definitions
- Modular tool creation and management

## Running the Project

Execute the Jupyter notebooks in the following order:
1. `main.ipynb` - Main project implementation
2. `notebook/gemini_api.ipynb` - API configuration and testing

## Development Notes

The project uses LangGraph's StateGraph to define multi-step workflows with:
- Custom state management
- Tool integration
- Message-based communication
- Asynchronous execution capabilities 
