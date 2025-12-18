#!/usr/bin/env python3
"""Tests for verify_llm_docs.py"""

from __future__ import annotations

import os
import sys
import tempfile

from pathlib import Path

import pytest

# Make `src/` importable when tests are executed without installing the package.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from llm_txt_tools.verify_llm_docs import (  # noqa: E402
    collect_section_file_order,
    sort_llm_file,
    VerifyOptions,
    verify,
)


def test_sort_llm_file_basic() -> None:
    """Test that sort_llm_file correctly sorts filenames within sections."""
    # Create a temporary directory and LLM.txt file
    with tempfile.TemporaryDirectory() as tmpdir:
        llm_file = Path(tmpdir) / "LLM.txt"

        # Write unsorted content
        content = """This is a preamble.

### /workspace/test/dir1

zebra.py - Description for zebra file.

apple.py - Description for apple file.
This continues on another line.

monkey.py - Description for monkey.

### /workspace/test/dir2

delta.py - Delta description.

alpha.py - Alpha description.

"""
        llm_file.write_text(content)

        # Sort the file
        sort_llm_file(str(llm_file), tmpdir)

        # Read back and verify
        result = llm_file.read_text()

        # Check that preamble is preserved
        assert "This is a preamble." in result

        # Parse to verify order
        section_order = collect_section_file_order(str(llm_file), tmpdir)

        dir1_abs = os.path.normpath(os.path.abspath("/workspace/test/dir1"))
        dir2_abs = os.path.normpath(os.path.abspath("/workspace/test/dir2"))

        # Verify alphabetical order in each section
        assert section_order[dir1_abs] == ["apple.py", "monkey.py", "zebra.py"]
        assert section_order[dir2_abs] == ["alpha.py", "delta.py"]


def test_sort_llm_file_preserves_multiline_descriptions() -> None:
    """Test that multi-line descriptions are preserved during sorting."""
    with tempfile.TemporaryDirectory() as tmpdir:
        llm_file = Path(tmpdir) / "LLM.txt"

        content = """### /workspace/test

zebra.py - First line of zebra.
Second line of zebra.
Third line of zebra.

apple.py - First line of apple.

"""
        llm_file.write_text(content)

        # Sort the file
        sort_llm_file(str(llm_file), tmpdir)

        result = llm_file.read_text()

        # Verify multi-line description is preserved and appears before zebra
        lines = result.split("\n")
        apple_idx = next(i for i, line in enumerate(lines) if "apple.py" in line)
        zebra_idx = next(i for i, line in enumerate(lines) if "zebra.py" in line)

        # Apple should come before zebra
        assert apple_idx < zebra_idx

        # Check multi-line content is preserved
        assert "Second line of zebra" in result
        assert "Third line of zebra" in result


def test_sort_llm_file_already_sorted() -> None:
    """Test that already sorted file remains unchanged."""
    with tempfile.TemporaryDirectory() as tmpdir:
        llm_file = Path(tmpdir) / "LLM.txt"

        content = """### /workspace/test

apple.py - Description for apple.

banana.py - Description for banana.

cherry.py - Description for cherry.

"""
        llm_file.write_text(content)

        # Sort the file
        sort_llm_file(str(llm_file), tmpdir)

        llm_file.read_text()

        # Content should be essentially the same (modulo whitespace normalization)
        section_order = collect_section_file_order(str(llm_file), tmpdir)
        test_dir_abs = os.path.normpath(os.path.abspath("/workspace/test"))
        assert section_order[test_dir_abs] == ["apple.py", "banana.py", "cherry.py"]


def test_verify_with_fix_sorting_integration() -> None:
    """Integration test: verify with fix_sorting flag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test Python files
        test_dir = tmpdir_path / "test"
        test_dir.mkdir()
        (test_dir / "zebra.py").write_text("# Zebra")
        (test_dir / "apple.py").write_text("# Apple")

        # Create unsorted LLM.txt
        llm_file = tmpdir_path / "LLM.txt"
        content = f"""### {test_dir}

zebra.py - Zebra module.

apple.py - Apple module.

"""
        llm_file.write_text(content)

        # Run verify with fix_sorting
        exit_code = verify(
            repo_root=str(tmpdir_path),
            llm_file_path=str(llm_file),
            options=VerifyOptions(enforce_two_sentences=False, fix_sorting=True),
        )

        # Verify files are now sorted
        section_order = collect_section_file_order(str(llm_file), str(tmpdir_path))
        test_dir_abs = os.path.normpath(str(test_dir))
        assert section_order[test_dir_abs] == ["apple.py", "zebra.py"]

        # Should pass validation
        assert exit_code == 0


def test_verify_detects_repeated_headers_and_fix_sorting_merges() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        test_dir = tmpdir_path / "test"
        test_dir.mkdir()
        (test_dir / "a.py").write_text("# A")
        (test_dir / "b.py").write_text("# B")

        llm_file = tmpdir_path / "LLM.txt"
        header = f"### {test_dir}"

        # Repeat the same header directory twice; this should be rejected.
        llm_file.write_text(
            f"""{header}

b.py - Two sentences. Still two sentences.

{header}

a.py - Two sentences. Still two sentences.

"""
        )

        exit_code_before = verify(
            repo_root=str(tmpdir_path),
            llm_file_path=str(llm_file),
            options=VerifyOptions(enforce_two_sentences=False),
        )
        assert exit_code_before == 1

        # With fix_sorting enabled, the repeated header should be merged away.
        exit_code_after = verify(
            repo_root=str(tmpdir_path),
            llm_file_path=str(llm_file),
            options=VerifyOptions(enforce_two_sentences=False, fix_sorting=True),
        )
        assert exit_code_after == 0

        merged = llm_file.read_text()
        assert merged.count(header) == 1

        section_order = collect_section_file_order(str(llm_file), str(tmpdir_path))
        test_dir_abs = os.path.normpath(str(test_dir))
        assert section_order[test_dir_abs] == ["a.py", "b.py"]


def test_verify_detects_duplicate_file_entries() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        test_dir = tmpdir_path / "test"
        test_dir.mkdir()
        (test_dir / "dup.py").write_text("# Duplicated")

        llm_file = tmpdir_path / "LLM.txt"
        llm_file.write_text(
            f"""### {test_dir}

dup.py - First summary sentence. Second summary sentence.

dup.py - First summary sentence. Second summary sentence.

"""
        )

        exit_code = verify(
            repo_root=str(tmpdir_path),
            llm_file_path=str(llm_file),
            options=VerifyOptions(enforce_two_sentences=False),
        )
        assert exit_code == 1


def test_verify_enforce_exact_two_sentences_ignores_symbols_block() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        test_dir = tmpdir_path / "test"
        test_dir.mkdir()
        (test_dir / "mod.py").write_text("# Module")

        llm_file = tmpdir_path / "LLM.txt"
        llm_file.write_text(
            f"""### {test_dir}

mod.py - First sentence. Second sentence.
Symbols:
  - Functions: foo (L1), bar (L2)

"""
        )

        exit_code = verify(
            repo_root=str(tmpdir_path),
            llm_file_path=str(llm_file),
            options=VerifyOptions(
                enforce_two_sentences=False,
                enforce_exact_two_sentences=True,
                enforce_sorted=True,
            ),
        )
        assert exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
