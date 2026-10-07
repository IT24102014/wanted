# Wanted

A static news aggregator for Tech, Politics, and Pop Culture. A Python script collects headlines from RSS feeds into `data/news.json`, and `index.html` displays them. Headlines, short snippets, and links go back to the original publishers.

## Run locally
```bash
pip install -r requirements.txt
python fetch_news.py          # writes data/news.json
python -m http.server 8000    # open http://localhost:8000
```

## Deploy (free)
1. Push this folder to a GitHub repo.
2. Settings > Pages > deploy from the `main` branch, root folder.
3. Settings > Actions > General > allow read and write permissions for workflows.
4. The workflow in `.github/workflows/update.yml` refreshes the news every 30 minutes. Run it once by hand from the Actions tab.

## Customize
Add or remove sources in `feeds.json` (`category` is `tech`, `politics`, or `pop`). Set a real contact URL in `USER_AGENT` inside `fetch_news.py`.
