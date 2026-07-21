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

for data in all_posts:
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

    author_tags_html = "".join(
        f"<span>{html.escape(tag)}</span>"
        for tag in data.get("author_tags", [])
    )

    related_posts_html = "".join(
        f'''
        <a class="related-card" href="/insights/{html.escape(p["slug"])}.html">
          <div class="tag">{html.escape(p.get("category", ""))}</div>
          <div>{html.escape(p.get("title", ""))}</div>
        </a>
        '''
        for p in data.get("related_posts", [])
    )

    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": data.get("title", ""),
        "description": data.get("deck", ""),
        "author": {
            "@type": "Person",
            "name": data.get("author", ""),
            "jobTitle": data.get("author_title", ""),
            "worksFor": {
                "@type": "Organization",
                "name": "MindMach"
            }
        },
        "publisher": {
            "@type": "Organization",
            "name": "MindMach",
            "url": "https://mindmach.in"
        },
        "datePublished": data.get("date", ""),
        "dateModified": data.get("date_modified", data.get("date", "")),
        "mainEntityOfPage": f"https://mindmach.in/insights/{data.get('slug', '')}/",
        "keywords": data.get("keywords", [])
    }

    html_output = post_template.safe_substitute(
        slug=html.escape(data.get("slug", "")),
        title=html.escape(data.get("title", "")),
        meta_title=html.escape(data.get("meta_title", data.get("title", "") + " | MindMach")),
        meta_description=html.escape(data.get("meta_description", data.get("deck", ""))),
        deck=html.escape(data.get("deck", "")),
        category=html.escape(data.get("category", "")),
        section_name=html.escape(data.get("section_name", data.get("category", ""))),
        findings=findings_html,
        sections=sections_html,
        pull_quote=html.escape(data.get("pull_quote", "")),
        takeaways=takeaways_html,
        author=html.escape(data.get("author", "")),
        author_title=html.escape(data.get("author_title", "")),
        author_linkedin=html.escape(data.get("author_linkedin", "#")),
        author_image=html.escape(data.get("author_image", "/placeholder-5.jpg")),
        author_tags_html=author_tags_html,
        related_posts_html=related_posts_html,
        cta_title=html.escape(data.get("cta_title", "Need senior engineering talent fast?")),
        cta_text=html.escape(data.get("cta_text", "Tell us what you need and we’ll send relevant profiles quickly.")),
        cta_link=html.escape(data.get("cta_link", "/#contact")),
        date=html.escape(data.get("date", "")),
        schema_json=json.dumps(schema, ensure_ascii=False)
    )

    (OUT_DIR / f"{data['slug']}.html").write_text(html_output, encoding="utf-8")

cards_html = "".join(
    f'''
    <a class="card" href="/insights/{html.escape(p["slug"])}.html">
      <div class="card-tag">{html.escape(p.get("category", ""))}</div>
      <h2 class="card-title">{html.escape(p.get("title", ""))}</h2>
      <p class="card-deck">{html.escape(p.get("deck", ""))}</p>
      <div class="card-meta">{html.escape(p.get("date", ""))}</div>
    </a>
    '''
    for p in all_posts
)

listing_output = listing_template.safe_substitute(cards=cards_html)
(OUT_DIR / "index.html").write_text(listing_output, encoding="utf-8")

print(f"Built {len(all_posts)} posts.")
