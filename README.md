# CheatGuard-AI
Official repository of CheatGuard AI agent

## Installing requirements
Run the following command for installing necessary python packages:

``$ pip install requests beautifulsoup4 googlesearch-python google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client``

If you want to test the code with the GPT-4o API, make sure to install ***openai*** library for Python:
``$ pip install openai``

If you prefer working with a local Large Language Model (LLM), make sure to install ***ollama*** for Python:
``$ pip install ollama``.
As well as installing it in your system (Refer to Ollama's [documentation](https://ollama.com/)).

## Selecting an LLM
This repository offers two versions of the code, one with **GPT-4o** using ***Open AI API***, and the other one with a **local LLM** using ***Ollama***.
Feel free to use the one that suits you best.

### For Cheatguard-GPT
Use your own **Open AI API-key**.

For best practices, create a variable ***OPENAI_API_KEY*** under a ***.env*** file.

### For Cheatguard-LLM
This code uses ***llama3.2*** as a local model. This choice was made for resources constraints only, as ***llama3.2:latest*** takes 2.0 GB of storage; whereas ***llama3.3:latest*** needs 43GB of free space (Read the documentation of [LLAMA3.2](https://ollama.com/library/llama3.2) and [LLAMA3.3](https://ollama.com/library/llama3.3) for more information).

Feel free to test it with other LLMs for better results (Refer to Ollama's [list of models](https://ollama.com/search)).

Once downloaded, modify the used model in **line 92** and in **line 114**: `response = ollama.chat(model="YOUR_MODEL_HERE", messages=[{"role": "user", "content": prompt}])`.

## Understanding the AI-agent's workflow
The AI Agent's pipeline encompasses **5 ordered steps**:

***1- Web Search:***

- A specific query is hard-coded to make the script search for the targetted content when started. The query that we opted for is: `f"Recent Papers about Cheating in Education in {datetime.now().strftime('%B') } {datetime.now().strftime('%Y')}"`, which allows to search for the latest articles published in the current month.

- The program performs a web search on Google with the query, and returns a list of found URLs, limited to a specified number of results, which by default is: `num_results=3`. **N.B:** The program allows to restrict the browsing to specific websites, or exclude some websites from the search, e.g: `search_google(user_query, num_results=3, include_sites["arxiv.org"],  exclude_sites=["researchgate.net"])`. We restricted the script from finding articles on [Research Gate](https://www.researchgate.net/) as it disallows the client from extracting content.

***2- Content Extraction:***

After finding interesting URLs, the script starts extracting meaningful content from them:

- The script removes the contents of unwanted sections, such as ***nav*** and ***footer***, and unwanted classes, such as ***extra-services*** of [Arxiv](https://www.arxiv.org). These parts will only overwhelm the LLM when processing the web content.
  
- After that, the script looks for the main content of a web page by searching for specific classes, such ***main*** or ***article***. The collected information from those sections is then passed to an LLM for filtering.

***3- Content Filtering:***

Once the web content is extracted from the URLs, the script starts filtering them:

- We use an LLM to **filter out** the relatively uncessary-information from the extracted content, based on the user's search query.
  
- The LLM is used to keep only the most-important information from the extracted contents, focusing on the **Cheating Technique** description, and its **prevention methods**
  
***4- Data Extraction***

- Using the local LLM to extract the main attributes of the extracted articles (Title, Authors, Description, Year)
  
***5- Email Sending***

- The Extracted Data is formatted in JSON

- The Data is sent by e-mail to the First Authors
