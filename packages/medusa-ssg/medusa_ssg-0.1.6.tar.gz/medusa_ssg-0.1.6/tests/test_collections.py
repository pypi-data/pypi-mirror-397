from datetime import datetime

from medusa.collections import PageCollection, TagCollection


class FakePage:
    def __init__(self, title, filename=None, group="", date=None, tags=None, draft=False):
        self.title = title
        self.filename = filename or f"{title.lower()}.md"
        self.group = group
        self.date = date or datetime(2024, 1, 1)
        self.tags = tags or []
        self.draft = draft


def test_page_collection_filters_and_latest():
    pages = PageCollection(
        [
            FakePage("B", filename="02_b.md", group="posts", date=datetime(2024, 1, 3), draft=True),
            FakePage("A", filename="01_a.md", group="posts", date=datetime(2024, 1, 2)),
            FakePage("C", filename="03_c.md", group="docs", date=datetime(2024, 1, 1), tags=["python"]),
        ]
    )
    # Pages are sorted by filename by default
    assert len(pages) == 3
    assert [p.title for p in pages] == ["A", "B", "C"]
    posts = pages.group("posts")
    assert [p.title for p in posts] == ["A", "B"]
    published = pages.published()
    assert [p.title for p in published] == ["A", "C"]
    drafts = pages.drafts()
    assert [p.title for p in drafts] == ["B"]
    latest = pages.latest(1)
    assert latest[0].title == "B"
    # sorted by filename ascending (default)
    sorted_asc = pages.sorted()
    assert [p.title for p in sorted_asc] == ["A", "B", "C"]
    # sorted by filename descending
    sorted_desc = pages.sorted(reverse=True)
    assert [p.title for p in sorted_desc] == ["C", "B", "A"]
    # sorted by title
    sorted_by_title = pages.sorted(key="title")
    assert [p.title for p in sorted_by_title] == ["A", "B", "C"]
    # sorted by date
    sorted_by_date = pages.sorted(key="date")
    assert [p.title for p in sorted_by_date] == ["C", "A", "B"]
    sorted_by_date_desc = pages.sorted(key="date", reverse=True)
    assert [p.title for p in sorted_by_date_desc] == ["B", "A", "C"]
    assert pages.with_tag("python")[0].title == "C"


def test_tag_collection_access():
    p1 = FakePage("T1")
    tags = TagCollection({"python": [p1]})
    assert tags["python"][0] is p1
    assert list(tags) == ["python"]
    assert list(tags.keys()) == ["python"]
    assert list(tags.values())[0][0] is p1
    assert list(tags.items())[0][0] == "python"
    assert tags.get("missing") is None
