import json
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import ollama
from datetime import datetime

import os
import pickle
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from dotenv import load_dotenv


### AI Agent Part

## Google Search
def search_google(query, num_results=3, include_sites=None, exclude_sites=None):
    """Search Google while including or excluding specific websites."""
    try:
        # Modify query to restrict/exclude sites
        if include_sites:
            site_filters = " OR ".join([f"site:{site}" for site in include_sites])
            query = f"({query}) ({site_filters})"
        
        if exclude_sites:
            site_filters = " ".join([f"-site:{site}" for site in exclude_sites])
            query = f"{query} {site_filters}"

        results = search(query, num_results=num_results)
        return list(results)

    except Exception as e:
        print(f"Google Search Error: {e}")
        return []


## Web Content Extraction
def extract_content_from_url(url):
    """Extract meaningful text from a webpage, prioritizing <article> and <main> sections or divs with role='main', while removing headers, footers, navs, scripts, and irrelevant divs."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unwanted elements: headers, footers, navigation bars, sidebars, scripts, styles
        for tag in ["header", "footer", "nav", "aside", "script", "style"]:
            for element in soup.find_all(tag):
                element.decompose()  # Remove from the DOM

        # Remove specific div classes that contain irrelevant content
        unwanted_classes = ["extra-services", "labstabs"]
        for class_name in unwanted_classes:
            for element in soup.find_all("div", class_=class_name):
                element.decompose()  # Remove from the DOM

        # Try to extract content from <main> or div[role="main"]
        main_content = soup.find("main") or soup.find("div", {"role": "main"})
        if main_content:
            extracted_text = main_content.get_text(separator="\n", strip=True)
        else:
            # If no <main> section is found, extract from the entire cleaned body
            extracted_text = soup.body.get_text(separator="\n", strip=True) if soup.body else ""

        # Limit extracted content to avoid LLM overload
        output = url + ' ' + extracted_text[:4000]
        return output

    except Exception as e:
        print(f"Failed to extract from {url}: {e}")
        return ""

## Web Content Filtering
def filter_relevant_content_with_llm(content, query):
    """Use LLM to filter content based on relevance to the user's query."""
    prompt = f"""
    You are an AI assistant tasked with extracting only the most relevant information from web content based on the user's query, focusing on the details about Cheating techniques, their prevention, and their mitigation. 

    User Query: {query}

    Content: 
    {content}

    Please filter out the irrelevant details and focus only on the detailed information about the Cheating technique, how is it performed or prevented. Keep in each answer the URL of the information you filtered. Do not add any information that is not mentioned in the content, be precise in ommiting what does not answer the user's query, especially filters and comments. If no details about cheating exists, return an empty string without keeping the URL. Answer with the filtered texts with their urls only, without adding introductions or comments to your answer. If any date related to the article is mentioned (submission date, publishing date, revision date, etc..) keep it. If multiple dates are mentioned with the same article, keep the most recent of them (such as the last revision date for example).
    """
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

## JSON Information Extraction
def extract_title_description_authors(summary):
    """Extract title, description, and authors from LLM's summary output."""
    prompt = f"""
    The following is a summary extracted from an article. Based on this summary, extract the title, description, authors, url, and year of the article. The description attribute is contains the details of the cheating technique described in the content and/or its prevention.

    Summary: 
    {summary}

    Provide the response as follows:
    {{
        "title": "<title>",
        "description": "<description>",
        "authors": ["<author1>", "<author2>", ...],
        "url": "<url>",
        "year": "<year>"
    }}
    Make sure the response is in JSON format and contains all required fields. If any information is missing, use an empty string or empty list where appropriate. Do not add any information or comment. Return only the JSON answer.
    """
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

## JSON Formatting
def format_json_output(title, description, authors, url, year):
    """Format the extracted information into JSON."""
    article = {
        "title": title,
        "description": description,
        "authors": authors,
        "year": year,
        "url": url,
    }
    return json.dumps(article, indent=4)


### EMAIL PART

## Authorizations for Sending Email
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
load_dotenv() # Loading .env

## GMAIL Authentifiction
def authenticate_gmail():
    """Authentify the user and returns his Credentials"""
    creds = None
    # Verify if the connection token exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If the credentials are invalid or does not exist, make a new connection
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Get Identifiers from .env
            client_id = os.getenv('CLIENT_ID')
            client_secret = os.getenv('CLIENT_SECRET')
            redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # URI of redirection

            # OAuth2 Flow Configuration
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uris": [redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                },
                SCOPES,
            )
            creds = flow.run_local_server(port=0)
        
        # Save Credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

## MIME Message Creation
def create_message(sender, to, subject, body):
    """Create a MIME message for sending."""
    message = MIMEText(body)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')}

## Message Sending
def send_message(service, user_id, message):
    """Sending an e-mail."""
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"E-mail sent successfully! Message ID: {message['id']}")
    except Exception as e:
        print(f"Errorr when sending email: {e}")

## EMAIL Sending
def send_email(sender, to, body):

    # Authentification
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    # Content of the E-mail
    subject = "CheatGuard Notification"

    # Email Cretion and Sending
    message = create_message(sender, to, subject, body)
    send_message(service, "me", message)

### MAIN Program
def main():

    # Step 1: Initialize Search Query
    user_query = f"Recent Papers about Cheating in Education and Academia in {datetime.now().strftime('%B') } {datetime.now().strftime('%Y')}"
    print(f"User query: {user_query}")

    # Step 2: Perform Google search with the user's query
    print("\nSearching...\n")
    urls = search_google(user_query, num_results=2, include_sites=["arxiv.org","springer.com"], exclude_sites=["researchgate.net"])
    print(f"URLs: {urls}")  # Debugging
    
    # Step 3: Extract information from the found URLs
    extracted_texts = [extract_content_from_url(url) for url in urls if url]
    print(f"Extracted texts: {extracted_texts}")  # Debugging
    
    # Step 4: Filter the content using LLM
    print("\nFiltering with LLM, might take few minutes...\n")
    filtered_texts = [filter_relevant_content_with_llm(text, user_query) for text in extracted_texts if text]
    print(f"Filtered texts: {filtered_texts}")  # Debugging
    
    # Step 5: Format the output to JSON and Send it through E-mail
    print("\nExtracting title, description, year, and authors...\n")
    extracted_info = [extract_title_description_authors(filtered_text) for filtered_text in filtered_texts if filtered_text]
    print(f"Extracted info: {extracted_info}")

    email_body = user_query # Email text
    for info in extracted_info:
        try:
            print(f"info: {info}")
            article_info = json.loads(info)
            title = article_info["title"]
            description = article_info["description"]
            authors = article_info["authors"]
            url = article_info["url"]
            year = article_info["year"]
            if title == "" : continue
            json_output = format_json_output(title, description, authors, url, year)
            print(f"json: {json_output}")
            email_body = email_body + '\n' + json_output

        except (json.JSONDecodeError, KeyError):
            print("Failed to extract information from the output.")
            continue

    sender = os.getenv('SENDER')
    receiver = os.getenv('RECEIVER')
    print("\nE-mail Preparation...\n")
    send_email(sender, receiver, email_body)


if __name__ == "__main__":
    main()