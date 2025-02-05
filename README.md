# CheatGuard-AI
Official repository of CheatGuard AI agent

## Installing requirements
Run the following command for installing necessary python packages:

$ pip install requests beautifulsoup4 ollama googlesearch-python

Make sure also to have **ollama** installed in your system (See https://ollama.com/)
## Selecting a local Ollama model
This code uses *llama3.2*. 

Feel free to test it with other Large Language Models (LLMs) for better results (See https://ollama.com/search).

Once downloaded, modify the used model in ***lines 63, 78, and 108***
## Understanding the AI-agent's workflow
The AI Agent's pipeline encompasses **5 ordered steps**:

***1- Web Search:***

- The user enters a specific search query, e.g: "Latest article of Author First Name Last Name published on Arxiv"

- The program performs a web search on Google

***2- Content Extraction***

- Removing contents of unwanted sections (Headers, Footers, etc...)

- Focusing on main articles and sections of a web page

***3- Content Filtering***

- Using the local LLM to filter the most important information from the extracted contents
  
***4- Data Extraction***

- Using the local LLM to extract the main attributes of the extracted articles (Title, Authors, Description, Year)
  
***5- Data Formatting***

- The Extracted Data is formatted in JSON

- The Data is sent by e-mail to the First Authors
