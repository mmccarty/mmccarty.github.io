# mikemccarty.io

This repository contains the MkDocs source for
[mikemccarty.io](https://mikemccarty.io). Python and MkDocs are managed with
[`uv`](https://docs.astral.sh/uv/).

## Local development

Install `uv`, then create the locked environment:

```shell
uv sync --locked
```

Start the local development server:

```shell
uv run mkdocs serve
```

Build the site with the same strict validation used in CI:

```shell
uv run --locked mkdocs build --strict
```

The generated site is written to `site/` and is not committed.

## Content

Pages and static assets live in `docs/`. The custom template that preserves the
site's original appearance lives in `overrides/main.html`.

Blog posts are managed by Material for MkDocs' built-in blog plugin. Add posts
under `docs/blog/posts/`, for example:

```text
docs/blog/posts/post-title.md
```

Each post should include at least a title and creation date:

```yaml
---
title: Post title
date:
  created: 2026-07-16
---
```

## Deployment

GitHub Actions builds and deploys the site after pushes to `gh-pages`. In the
repository's Pages settings, set the publishing source to **GitHub Actions**.
The workflow installs the environment from `uv.lock`, runs a strict MkDocs
build, and deploys the resulting Pages artifact.

The custom domain remains configured as `mikemccarty.io` through `docs/CNAME`
and the repository's GitHub Pages settings.
