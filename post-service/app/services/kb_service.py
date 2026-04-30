import json


# -------------------------------
# GET DATA FROM KB (JSON NOW)
# -------------------------------
def fetch_kb_posts():

    with open("app/data/kb_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])

    result = []

    for item in items:

        result.append({
            "title": item.get("title"),
            "summary": item.get("summary_raw"),
            "published_at": item.get("published_at"),
            "image": (item.get("images") or [None])[0]
        })

    return result