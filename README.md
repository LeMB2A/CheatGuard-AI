# CheatGuard-AI
Official repository of CheatGuard AI agent

## Installing requirements
Run the following command for installing necessary python packages:

``$ pip install requests beautifulsoup4 googlesearch-python google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client``

If you want to test the code with the GPT-4o API, make sure to install ***openai*** library for Python:
``$ pip install openai``

If you prefer working with a local Large Language Model (LLM), make sure to install ***ollama*** for Python:
``$ pip install ollama``.
As well as installing it in your system (See https://ollama.com/).

## Selecting an LLM
This repository offers two versions of the code, one with **GPT-4o** using ***Open AI API***, and the other one with a **local LLM** using ***Ollama***.
Feel free to use the one that suits you best.

### For Cheatguard-GPT
Use your own **Open AI API-key**.

For best practices, create a variable ***OPENAI_API_KEY*** under a ***.env*** file.

### For Cheatguad-LLM
This code uses ***llama3.2*** as a local model. This choice was made for resources constraints only, as ***llama3.2:latest*** takes 2.0 GB of storage; whereas ***llama3.3:latest*** needs 43GB of free space (Visit https://ollama.com/library/llama3.2 and https://ollama.com/library/llama3.3 for more information).

Feel free to test it with other LLMs for better results (Refer to https://ollama.com/search).

Once downloaded, modify the used model in **line 92** and in **line 114**: `response = ollama.chat(model="YOUR_MODEL_HERE", messages=[{"role": "user", "content": prompt}])`.

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
