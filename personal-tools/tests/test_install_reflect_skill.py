"""The reflect-skill installer, exercised against a throwaway HOME.

It writes to the user's real `~/.claude/skills/reflect/SKILL.md`. Unlike the
global-instructions installer this is a plain file copy -- a skill has no
existing content to splice into -- so the load-bearing tests are simpler:
the file lands, a stale copy gets backed up and replaced, and repeats are
no-ops.
"""

import os

import pytest

from tools import install_reflect_skill as installer


@pytest.fixture
def home(tmp_path, monkeypatch):
    root = tmp_path / "home"
    (root / ".claude").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(root))
    monkeypatch.setenv("USERPROFILE", str(root))  # Windows
    monkeypatch.setattr(os.path, "expanduser", lambda p: p.replace("~", str(root), 1))
    return root / ".claude"


def skill_md(home):
    return (home / "skills" / "reflect" / "SKILL.md").read_text(encoding="utf-8")


def test_it_works_from_nothing(home):
    assert installer.main([]) == 0
    text = skill_md(home)
    assert text.startswith("---\nname: reflect")
    assert "<!--" not in text.splitlines()[0]


def test_running_twice_changes_nothing(home):
    installer.main([])
    first = skill_md(home)
    installer.main([])
    assert skill_md(home) == first
    backup = home / "skills" / "reflect" / "SKILL.md.bak"
    assert not backup.exists() or backup.read_text(encoding="utf-8") == first


def test_check_and_diff_write_nothing(home):
    assert installer.main(["--check"]) == 0
    assert not (home / "skills" / "reflect" / "SKILL.md").exists()
    assert installer.main(["--diff"]) == 0
    assert not (home / "skills" / "reflect" / "SKILL.md").exists()


def test_a_stale_copy_is_backed_up_and_replaced(home):
    target_dir = home / "skills" / "reflect"
    target_dir.mkdir(parents=True)
    (target_dir / "SKILL.md").write_text("old draft\n", encoding="utf-8")

    installer.main([])

    assert (target_dir / "SKILL.md.bak").read_text(encoding="utf-8") == "old draft\n"
    assert skill_md(home).startswith("---\nname: reflect")


def test_it_refuses_a_machine_with_no_claude_home(tmp_path, monkeypatch):
    """A cloud container has no ~/.claude worth writing to; say so, do nothing."""

    empty = tmp_path / "nowhere"
    empty.mkdir()
    monkeypatch.setattr(os.path, "expanduser", lambda p: p.replace("~", str(empty), 1))
    assert installer.main([]) == 1


def test_the_source_explains_itself_only_to_the_repository():
    """The leading comment is for a reader of docs/, not part of the skill."""

    raw = open(installer.SOURCE, "r", encoding="utf-8").read()
    assert raw.lstrip().startswith("<!--")
    body = installer.load_source()
    assert body.startswith("---\nname: reflect")
    assert not body.startswith("<!--")


def test_the_installer_is_ascii_only():
    """Windows PowerShell 5.1 reads a BOM-less file as Windows-1252, and a single
    non-ASCII byte can stop a script parsing at all."""

    path = os.path.join("tools", "install_reflect_skill.py")
    assert all(b < 128 for b in open(path, "rb").read())


def test_the_skill_source_is_ascii_only():
    assert all(b < 128 for b in open(installer.SOURCE, "rb").read())
