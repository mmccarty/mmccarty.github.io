from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml


BLOG_POSTS_MARKER = "<!-- BLOG_POSTS -->"


@dataclass(frozen=True)
class Post:
    title: str
    published: date
    source_uri: str

    @property
    def formatted_date(self) -> str:
        return self.published.strftime("%b %d, %Y")


def _metadata(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}

    header, separator, _ = text.partition("\n---\n")
    if not separator:
        return {}

    metadata = yaml.safe_load(header.removeprefix("---\n"))
    return metadata if isinstance(metadata, dict) else {}


def _published_date(value: Any, path: Path) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    raise ValueError(f"{path}: post metadata requires a valid ISO date")


def _load_post(path: Path, docs_dir: Path) -> Post | None:
    metadata = _metadata(path)
    if metadata.get("post") is not True:
        return None

    title = metadata.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError(f"{path}: post metadata requires a non-empty title")

    return Post(
        title=title.strip(),
        published=_published_date(metadata.get("date"), path),
        source_uri=path.relative_to(docs_dir).as_posix(),
    )


def load_posts(docs_dir: str | Path) -> list[Post]:
    root = Path(docs_dir)
    posts = [
        post
        for path in root.rglob("*.md")
        if (post := _load_post(path, root)) is not None
    ]
    return sorted(posts, key=lambda post: post.published, reverse=True)


def _post_list(posts: list[Post]) -> str:
    return "\n".join(
        f"- [{post.title}]({post.source_uri}) {post.formatted_date}"
        for post in posts
    )


def on_page_markdown(markdown: str, page: Any, config: Any, **kwargs: Any) -> str:
    posts = load_posts(config["docs_dir"])

    if page.file.src_uri == "blog.md":
        return markdown.replace(BLOG_POSTS_MARKER, _post_list(posts))

    if page.meta.get("post") is True:
        post = next(
            (post for post in posts if post.source_uri == page.file.src_uri),
            None,
        )
        if post is None:
            raise ValueError(f"{page.file.src_uri}: unable to load post metadata")
        page.meta["formatted_date"] = post.formatted_date

    return markdown
