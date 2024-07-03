import os
import requests
from bs4 import BeautifulSoup

def read_urls(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def save_scraped_url(url, file_path):
    with open(file_path, 'a') as file:
        file.write(url + '\n')

def scrape_and_save(url, output_folder, scraped_urls_file):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    text_elements = []

    # Extract text from specific elements
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span']:
        for element in soup.find_all(tag):
            text_elements.append(element.get_text(strip=True))

    clean_text = '\n'.join(text_elements)
    if not clean_text:
        print(f"No relevant text found at {url}")
        return

    # # Extract innerText from the body tag
    # soup = BeautifulSoup(response.content, 'html.parser')
    # body = soup.find('body')
    # if body:
    #     clean_text = body.get_text(separator=' ', strip=True)
    # else:
    #     print(f"No body tag found in {url}")
    #     return

    # if not clean_text:
    #     print(f"No relevant text found at {url}")
    #     return

    # Define a valid filename based on the URL
    filename = url.replace('https://', '').replace('http://', '').replace('/', '_') + '.txt'
    output_path = os.path.join(output_folder, filename)

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(clean_text)

    save_scraped_url(url, scraped_urls_file)
    print(f"Saved content from {url} to {output_path}")

def main():
    urls_file = 'scrape_urls.txt'
    scraped_urls_file = 'scraped_urls.txt'
    output_folder = 'scraped_pages'

    os.makedirs(output_folder, exist_ok=True)

    # Read URLs to scrape
    urls_to_scrape = read_urls(urls_file)

    # Read already scraped URLs
    if os.path.exists(scraped_urls_file):
        scraped_urls = read_urls(scraped_urls_file)
    else:
        scraped_urls = []

    for url in urls_to_scrape:
        if url not in scraped_urls:
            scrape_and_save(url, output_folder, scraped_urls_file)
        else:
            print(f"Skipping already scraped URL: {url}")

if __name__ == '__main__':
    main()
