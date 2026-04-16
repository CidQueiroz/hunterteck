import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
url = "https://html.duckduckgo.com/html/"
data = {'q': 'escolas de idiomas macae rj contato email telefone'}

response = requests.post(url, data=data, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
results = soup.find_all('div', class_='result')

for r in results:
    title_a = r.find('a', class_='result__a')
    url_a = r.find('a', class_='result__url') 
    snippet = r.find('a', class_='result__snippet')
    if title_a:
        print(f"Title: {title_a.text}\nLink: {url_a.text.strip() if url_a else ''}\nSnippet: {snippet.text if snippet else ''}\n---")
