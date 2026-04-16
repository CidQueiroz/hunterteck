from duckduckgo_search import DDGS

ddgs = DDGS()
for backend in ['api', 'html', 'lite']:
    try:
        print(f"Testing {backend}...")
        results = list(ddgs.text("escolas em macaé rj", max_results=3, backend=backend))
        print(f"Found {len(results)} results")
        if results: print(results[0])
    except Exception as e:
        print(f"Error {backend}: {e}")

