import json
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import ollama

def search_google(query, num_results=2):
    """Search Google using the googlesearch package and return URLs."""
    try:
        results = search(query, num_results=num_results)
        return list(results)
    except Exception as e:
        print(f"Google Search Error: {e}")
        return []

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
        return extracted_text[:3000]

    except Exception as e:
        print(f"Failed to extract from {url}: {e}")
        return ""

def filter_relevant_content_with_llm(content, query):
    """Use LLM to filter content based on relevance to the user's query."""
    prompt = f"""
    You are an AI assistant tasked with extracting only the most relevant information from web content based on the user's query. 

    User Query: {query}

    Content: 
    {content}

    Please filter out the irrelevant details and focus only on the information that answers the user's query. Do not add any information that is not mentioned in the content, be precise in ommiting what does not answer the user's query, especially filters and comments. If no relevent answer exists, return an empty string. Answer with the filtered texts only without adding introductions or comments to your answer. If any date related to the article is mentioned (submission date, publishing date, revision date, etc..) keep it. If multiple dates are mentioned with the same article, keep the most recent of them (such as the last revision date).
    """
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

def extract_title_description_authors(summary):
    """Extract title, description, and authors from LLM's summary output."""
    prompt = f"""
    The following is a summary extracted from an article. Based on this summary, extract the title, description, authors, and year of the article.

    Summary: 
    {summary}

    Provide the response as follows:
    {{
        "title": "<title>",
        "description": "<description>",
        "authors": ["<author1>", "<author2>", ...],
        "year": "<year>"
    }}
    Make sure the response is in JSON format and contains all required fields. If any information is missing, use an empty string or empty list where appropriate. Do not add any information or comment. Return only the JSON answer.
    """
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

def format_json_output(title, description, authors, year):
    """Format the extracted information into JSON."""
    article = {
        "title": title,
        "description": description,
        "authors": authors,
        "year": year
    }
    return json.dumps(article, indent=4)

def main():
    print("Welcome to CheatGuard AI, use direct queries such as: Articles of January 2025 on Arxiv about Cheating in Education\n")
    user_query = input("Enter your search query: ")
    
    # Step 1: Perform Google search with the user's query
    print("\nSearching...\n")
    urls = search_google(user_query, num_results=3)
    print(f"URLs: {urls}")  # Debugging
    
    # Step 2: Extracting information from the found URLs
    extracted_texts = [extract_content_from_url(url) for url in urls if url]
    print(f"Extracted texts: {extracted_texts}")  # Debugging
    
    # Step 3: Filtering the content using LLM
    print("\nFiltering with LLM, might take few minutes...\n")  # Debugging
    filtered_texts = [filter_relevant_content_with_llm(text, user_query) for text in extracted_texts if text]
    print(f"Filtered texts: {filtered_texts}")  # Debugging
    
    # Step 4: Extract title, description, and authors from LLM's summary
    print("\nExtracting title, description, and authors...\n")
    extracted_info = [extract_title_description_authors(filtered_text) for filtered_text in filtered_texts if filtered_text]
    print(f"Extracted info: {extracted_info}")

    # Step 5: Format and print the results as JSON
    for info in extracted_info:
        try:
            article_info = json.loads(info)
            title = article_info["title"]
            description = article_info["description"]
            authors = article_info["authors"]
            year = article_info["year"]
        except (json.JSONDecodeError, KeyError):
            print("Failed to extract information from the summary.")
            return
        
        json_output = format_json_output(title, description, authors, year)
        print("\n=== JSON Output ===\n")
        print(json_output)
    

if __name__ == "__main__":
    main()