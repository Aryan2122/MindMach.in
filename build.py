import json
from pathlib import Path

POSTS_DIR = Path("content/posts")
OUT_DIR = Path("site/insights")
OUT_DIR.mkdir(exist_ok=True)

post_template = Path("templates/post.html").read_text()
listing_template = Path("templates/listing.html").read_text()

all_posts = []
for f in POSTS_DIR.glob("*.json"):
    data = json.loads(f.read_text())
    all_posts.append(data)

    sections_html = "".join(
        f"<h2>{s['heading']}</h2><p>{s['body']}</p>" for s in data["sections"]
    )
    findings_html = "".join(f"<li>{k}</li>" for k in data["key_findings"])
    takeaways_html = "".join(f"<li>{t}</li>" for t in data["key_takeaways"])

    html = post_template.format(
        title=data["title"], deck=data["deck"], category=data["category"],
        findings=findings_html, sections=sections_html,
        pull_quote=data["pull_quote"], takeaways=takeaways_html,
        author=data["author"], author_title=data["author_title"], date=data["date"]
    )
    (OUT_DIR / f"{data['slug']}.html").write_text(html)

cards_html = "".join(
    f'<a href="/insights/{p["slug"]}.html"><h3>{p["title"]}</h3><p>{p["deck"]}</p></a>'
    for p in all_posts
)
(OUT_DIR / "index.html").write_text(listing_template.format(cards=cards_html))
print(f"Built {len(all_posts)} posts.")
