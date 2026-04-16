from googlesearch import search
try:
    results = list(search("escolas particulares macae rj contato email", num_results=5, advanced=True))
    for r in results:
        print(r.title, r.url, r.description)
except Exception as e:
    print(f"Error: {e}")
