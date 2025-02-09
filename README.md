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

***1- Query Formulation:***

The script starts by formulating a precise search query:

- The query is **hard-coded** to make the script search for the targetted content when started.
  
- The query that we opted for is: `f"Recent Papers about Cheating in Education in {datetime.now().strftime('%B') } {datetime.now().strftime('%Y')}"`, which allows to search for the latest articles published in the **current month**.

- Feel free to modify the query in order to find the **optimal** formulation.

***2- Web Search***

After defining a search query:

- The program performs a web search on **Google** with the query, and returns a list of found URLs.

- The number of URLs is a **parameter** that can be modified based on the need. The **default value** is: `num_results=3`.

- The program allows to **restrict** the browsing to specific websites, or **exclude** some websites from the search, e.g: `search_google(user_query, num_results=3, include_sites["arxiv.org"],  exclude_sites=["researchgate.net"])`. We restricted the script from finding articles on [Research Gate](https://www.researchgate.net/) as it disallows the client from extracting content.

***3- Content Extraction:***

After finding interesting URLs, the script starts extracting meaningful content from them:

- The script removes the contents of unwanted sections, such as ***nav*** and ***footer***, and unwanted classes, such as ***extra-services*** of [Arxiv](https://www.arxiv.org). These parts will only overwhelm the LLM when processing the web content.
  
- After that, the script looks for the main content of a web page by searching for specific classes, such as ***main*** or ***article*** sections: `main_content = soup.find("main") or soup.find("article", id="main") or soup.find("div", {"role": "main"}) or soup.find("div", {"id": "main-content"}) or soup.find("div", class_="ltx_page_content")`.

-   The collected information from those sections is then passed to an LLM for filtering.

***4- Content Filtering:***

Once the web content is extracted from the URLs, the script starts filtering them:

- We use an LLM to **filter out** the relatively uncessary-information from the extracted content, based on the user's search query.
  
- The LLM is used to keep only the most-important information from the extracted contents, focusing on the **Cheating Technique** description, and its **prevention methods**
  
***5- Data Formatting and E-mail Sending***

After filtering the extracted data:

- We use the LLM to **format** the main attributes of the found articles to **JSON** format, focusing on the title, description, authors, URL, and year of publication.

- The formatted output is sent **by e-mail** to the **administrator** in order to validate the information before updating the **Knowledge Base**.

- The e-mail is sent by using **OAuth2** with ***Gmail API***. The details on how to configure it are detailed in the next section.

## Configuring Google Cloud Console
Please follow the steps below to create your Credentials:

1. **Access Google Cloud Console**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project or select an existing project.

2. **Enable the Gmail API**:
   - In the left-hand menu, go to **"APIs & Services" > "Library"**.
   - Search for **"Gmail API"** and click **"Enable"**.

3. **Configure the OAuth Consent Screen**:
   - Go to **"APIs & Services" > "OAuth Consent Screen"**.
   - Choose **"External"** (or **"Internal"** if you're in a Google Workspace organization).
   - Fill in the required information (application name, support email, etc.).
   - Add the necessary scopes (permissions):
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.compose`
   - Save and continue.

4. **Create OAuth2 Credentials**:
   - Go to **"APIs & Services" > "Credentials"**.
   - Click on **"Create Credentials"** and choose **"OAuth Client ID"**.
   - Select **"Desktop App"** as the application type.
   - Give a name to your client ID.
   - Download the JSON credentials file after creation. This file contains your `client_id` and `client_secret`.
   - Add the two variables ***CLIENT_ID*** and ***CLIENT_SECRET*** to your **.env** file.
  
  ## Automating the Execution

  Once everything is working, it is preferable to make the script's execution periodical automatically.

  - 
