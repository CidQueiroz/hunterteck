import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = "https://www.bing.com/search"
params = {'q': 'escolas de idiomas macae rj contato email telefone'}

response = requests.get(url, params=params, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
results = soup.find_all('li', class_='b_algo')

for r in results:
    title = r.find('h2').text if r.find('h2') else ''
    link = r.find('a')['href'] if r.find('a') else ''
    snippet = r.find('p').text if r.find('p') else ''
    print(f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n---")
