import json
import html
from pathlib import Path
from string import Template

POSTS_DIR = Path("content/posts")
OUT_DIR = Path("site/insights")
OUT_DIR.mkdir(exist_ok=True, parents=True)

post_template = Template(Path("templates/post.html").read_text(encoding="utf-8"))
listing_template = Template(Path("templates/listing.html").read_text(encoding="utf-8"))

all_posts = []

for f in sorted(POSTS_DIR.glob("*.json")):
    data = json.loads(f.read_text(encoding="utf-8"))
    all_posts.append(data)

    sections_html = "".join(
        f"<section><h2>{html.escape(s['heading'])}</h2><p>{html.escape(s['body'])}</p></section>"
        for s in data.get("sections", [])
    )

    findings_html = "".join(
        f"<li>{html.escape(item)}</li>"
        for item in data.get("key_findings", [])
    )

    takeaways_html = "".join(
        f"<li>{html.escape(item)}</li>"
        for item in data.get("key_takeaways", [])
    )

    html_output = post_template.safe_substitute(
        title=html.escape(data.get("title", "")),
        deck=html.escape(data.get("deck", "")),
        category=html.escape(data.get("category", "")),
        findings=findings_html,
        sections=sections_html,
        pull_quote=html.escape(data.get("pull_quote", "")),
        takeaways=takeaways_html,
        author=html.escape(data.get("author", "")),
        author_title=html.escape(data.get("author_title", "")),
        date=html.escape(data.get("date", "")),
    )

    (OUT_DIR / f"{data['slug']}.html").write_text(html_output, encoding="utf-8")

cards_html = "".join(
    f'<a class="insight-card" href="/insights/{html.escape(p["slug"])}.html">'
    f'<div class="ic-tag">{html.escape(p.get("category", ""))}</div>'
    f'<h3 class="ic-title">{html.escape(p.get("title", ""))}</h3>'
    f'<p class="ic-excerpt">{html.escape(p.get("deck", ""))}</p>'
    f'</a>'
    for p in all_posts
)
)

listing_output = listing_template.safe_substitute(cards=cards_html)
(OUT_DIR / "index.html").write_text(listing_output, encoding="utf-8")

print(f"Built {len(all_posts)} posts.")
