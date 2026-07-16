from __future__ import annotations

import importlib
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BlogHookTests(unittest.TestCase):
    def _write_post(
        self,
        docs_dir: Path,
        relative_path: str,
        *,
        title: str | None,
        date: str,
    ) -> None:
        path = docs_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        title_line = "" if title is None else f'title: "{title}"\n'
        path.write_text(
            f"---\npost: true\n{title_line}date: {date}\n---\n\nPost body.\n",
            encoding="utf-8",
        )

    def test_load_posts_sorts_newest_first_and_formats_dates(self) -> None:
        blog = importlib.import_module("blog")

        with tempfile.TemporaryDirectory() as directory:
            docs_dir = Path(directory)
            self._write_post(
                docs_dir,
                "2021/05/26/older.md",
                title="Older",
                date="2021-05-26",
            )
            self._write_post(
                docs_dir,
                "2024/01/02/newer.md",
                title="Newer",
                date="2024-01-02",
            )

            posts = blog.load_posts(docs_dir)

        self.assertEqual([post.title for post in posts], ["Newer", "Older"])
        self.assertEqual(posts[0].formatted_date, "Jan 02, 2024")
        self.assertEqual(posts[0].source_uri, "2024/01/02/newer.md")

    def test_load_posts_rejects_a_missing_title(self) -> None:
        blog = importlib.import_module("blog")

        with tempfile.TemporaryDirectory() as directory:
            docs_dir = Path(directory)
            self._write_post(
                docs_dir,
                "2024/01/02/untitled.md",
                title=None,
                date="2024-01-02",
            )

            with self.assertRaisesRegex(ValueError, "untitled.md.*title"):
                blog.load_posts(docs_dir)

    def test_load_posts_rejects_an_invalid_date(self) -> None:
        blog = importlib.import_module("blog")

        with tempfile.TemporaryDirectory() as directory:
            docs_dir = Path(directory)
            self._write_post(
                docs_dir,
                "2024/01/02/bad-date.md",
                title="Bad date",
                date="January 2",
            )

            with self.assertRaisesRegex(ValueError, "bad-date.md.*ISO date"):
                blog.load_posts(docs_dir)


class SiteBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mkdocs_config = ROOT / "mkdocs.yml"
        if not cls.mkdocs_config.is_file():
            raise AssertionError("mkdocs.yml must define the migrated site")

        mkdocs = shutil.which("mkdocs")
        if mkdocs is None:
            raise AssertionError("mkdocs must be installed in the test environment")

        cls._temporary_directory = tempfile.TemporaryDirectory()
        cls.site_dir = Path(cls._temporary_directory.name) / "site"
        subprocess.run(
            [
                mkdocs,
                "build",
                "--strict",
                "--config-file",
                str(cls.mkdocs_config),
                "--site-dir",
                str(cls.site_dir),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "_temporary_directory"):
            cls._temporary_directory.cleanup()

    def test_build_preserves_legacy_pages_and_assets(self) -> None:
        expected_paths = [
            "index.html",
            "about.html",
            "blog.html",
            "talks.html",
            "cv.html",
            "work.html",
            "2021/05/26/time-for-a-change.html",
            "assets/css/normalize.css",
            "assets/css/skeleton.css",
            "assets/css/styles.css",
            "assets/images/mike.jpg",
            "assets/images/SPIGOT_Ter5_050505_PSR_1748-24ae.pfd.ps",
            "CNAME",
        ]

        for relative_path in expected_paths:
            with self.subTest(path=relative_path):
                self.assertTrue((self.site_dir / relative_path).is_file())

        self.assertEqual(
            (self.site_dir / "CNAME").read_text(encoding="utf-8").strip(),
            "mikemccarty.io",
        )

    def test_blog_lists_the_post_and_date(self) -> None:
        html = (self.site_dir / "blog.html").read_text(encoding="utf-8")

        self.assertIn('href="2021/05/26/time-for-a-change.html"', html)
        self.assertIn("Time for a Change", html)
        self.assertIn("May 26, 2021", html)

    def test_nested_post_uses_the_custom_layout(self) -> None:
        html = (
            self.site_dir / "2021/05/26/time-for-a-change.html"
        ).read_text(encoding="utf-8")

        self.assertIn("Mike McCarty - Blog", html)
        self.assertIn("Posted on: May 26, 2021", html)
        self.assertIn('../../../assets/css/styles.css', html)
        self.assertIn("G-94RENSJC31", html)

    def test_rendered_html_contains_no_jekyll_syntax(self) -> None:
        for path in self.site_dir.rglob("*.html"):
            html = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(self.site_dir)):
                self.assertNotIn("{%", html)
                self.assertNotIn("{{ page.", html)
                self.assertNotIn("layout: default", html)


class ProjectConfigurationTests(unittest.TestCase):
    def test_github_pages_workflow_uses_uv_and_official_pages_actions(self) -> None:
        workflow_path = ROOT / ".github/workflows/deploy.yml"
        self.assertTrue(workflow_path.is_file())
        workflow = workflow_path.read_text(encoding="utf-8")

        expected_fragments = [
            "gh-pages",
            "astral-sh/setup-uv@",
            "uv sync --locked",
            "uv run --locked mkdocs build --strict",
            "actions/configure-pages@",
            "actions/upload-pages-artifact@",
            "actions/deploy-pages@",
            "pages: write",
            "id-token: write",
        ]
        for fragment in expected_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, workflow)

    def test_readme_documents_the_uv_workflow(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for command in (
            "uv sync --locked",
            "uv run mkdocs serve",
            "uv run --locked mkdocs build --strict",
        ):
            with self.subTest(command=command):
                self.assertIn(command, readme)
        self.assertIn("GitHub Actions", readme)

    def test_generated_outputs_are_not_tracked(self) -> None:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        tracked_paths = result.stdout.splitlines()

        generated_prefixes = ("_site/", "site/", ".venv/", "docs/superpowers/")
        for prefix in generated_prefixes:
            with self.subTest(prefix=prefix):
                self.assertFalse(
                    any(path.startswith(prefix) for path in tracked_paths),
                    f"{prefix} should not be committed",
                )


if __name__ == "__main__":
    unittest.main()
