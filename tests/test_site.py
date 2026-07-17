from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
            "blog/index.html",
            "talks.html",
            "cv.html",
            "work.html",
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

    def test_rendered_html_preserves_original_theme(self) -> None:
        expected_pages = [
            "index.html",
            "blog/index.html",
            "blog/2026/07/16/test-post.html",
        ]

        for relative_path in expected_pages:
            html = (self.site_dir / relative_path).read_text(encoding="utf-8")
            with self.subTest(path=relative_path):
                self.assertIn('class="container"', html)
                self.assertIn("assets/css/normalize.css", html)
                self.assertIn("assets/css/skeleton.css", html)
                self.assertIn("assets/css/styles.css", html)
                self.assertNotIn('class="md-header', html)

    def test_blog_omits_the_removed_post(self) -> None:
        html = (self.site_dir / "blog/index.html").read_text(encoding="utf-8")

        self.assertNotIn('href="2021/05/26/time-for-a-change.html"', html)
        self.assertNotIn("Time for a Change", html)
        self.assertNotIn("May 26, 2021", html)

    def test_blog_lists_the_test_post(self) -> None:
        html = (self.site_dir / "blog/index.html").read_text(encoding="utf-8")

        self.assertIn('href="2026/07/16/test-post.html"', html)
        self.assertEqual(html.count('href="2026/07/16/test-post.html"'), 1)
        self.assertIn("Test Post", html)

    def test_blog_post_output_is_removed(self) -> None:
        self.assertFalse(
            (self.site_dir / "2021/05/26/time-for-a-change.html").exists()
        )

    def test_test_post_is_generated_by_the_blog_plugin(self) -> None:
        post_path = self.site_dir / "blog/2026/07/16/test-post.html"
        self.assertTrue(post_path.is_file())

        html = post_path.read_text(encoding="utf-8")
        self.assertIn("Test Post", html)
        self.assertRegex(html, r"1\s+min(?:ute)?\s+read")
        self.assertIn(
            "This is a test post for verifying the MkDocs blog plugin.",
            html,
        )

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
        self.assertRegex(workflow, r"astral-sh/setup-uv@v\d+\.\d+\.\d+")

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

    def test_blog_uses_material_builtin_blog_plugin(self) -> None:
        mkdocs_config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
        project_config = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn("mkdocs-material", project_config)
        self.assertNotIn("mkdocs-blog-plugin", project_config)
        self.assertIn("name: mkdocs", mkdocs_config)
        self.assertIn("custom_dir: overrides", mkdocs_config)
        self.assertIn("- blog", mkdocs_config)
        self.assertIn(
            'blog = "material.plugins.blog.plugin:BlogPlugin"',
            project_config,
        )
        self.assertNotIn("folder:", mkdocs_config)
        self.assertNotIn("hooks:", mkdocs_config)
        self.assertFalse((ROOT / "blog.py").exists())
        self.assertTrue((ROOT / "docs/blog/index.md").is_file())
        self.assertTrue((ROOT / "docs/blog/posts/test-post.md").is_file())

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
