import re
import sys
from pathlib import Path
from textwrap import dedent

from lxml import etree

from .convert import to_markdown


def _one(key):
    return lambda el: el.find(key, el.nsmap).text


def _many(key):
    return lambda el: [_.text for _ in el.findall(key, el.nsmap)]


def _read_fields(el, fields):
    return {name: key(el) for name, key in fields.items()}


ITEM_FIELDS = {
    "content": _one("content:encoded"),
    "date": _one("wp:post_date"),
    "date_local": _one("pubDate"),
    "link": _one("link"),
    "status": _one("wp:status"),
    "tags": _many("category"),
    "title": _one("title"),
    "type": _one("wp:post_type"),
}


def header(info):
    meta = dedent(
        f"""
            title: "{info['title']}"
            date: {info['date_local']}
            draft: {'true' if info['status'] == 'draft' else 'false'}
            """
    ).strip()

    # 'none' isn't a real tag
    tags = [tag for tag in info["tags"] if tag != "none"]
    if tags:
        meta += '\ntags: [ "' + '", "'.join(tags) + '" ]'

    return f"---\n{meta}\n---"


def write_item(path, *content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n\n".join(content))


def file_name(info, site_url):
    if info["status"] == "publish":
        stem = info["link"].replace(site_url, "").strip("/")
        if stem == "":
            return "index.md"
        else:
            return re.sub(r"(\d{4})/(\d{2})/(\d{2})/", r"\1-\2-\3-", stem) + ".md"
    elif info["status"] == "draft":
        return (
            info["date"][:10]
            + "-"
            + info["title"].lower().translate(str.maketrans(" '", "--"))
            + ".md"
        )


def convert_item(item, site_url):
    info = _read_fields(item, ITEM_FIELDS)
    if info["type"] in ("post", "page"):
        path = Path("content") / f'{info["type"]}s' / file_name(info, site_url)
        write_item(path, header(info), to_markdown(info["content"]))


def convert_items(xml):
    doc = etree.parse(str(xml))
    channel = doc.find("channel")
    site_url = _one("wp:base_blog_url")(channel)

    for item in doc.iter("item"):
        convert_item(item, site_url)


def main():
    for xml in sys.argv[1:]:
        print(f"Processing: {xml}")
        convert_items(xml)
