import os
import re
import ast
from pathlib import Path

# Configuration
DOCS_DIR = Path("docs")
REPORT_FILE = "doc_code_analysis_report.md"

# Rules
DEPRECATED_APIS = {
    "send_message_async": "Use `send_message` (async) or `send_message_sync` instead.",
}

INCORRECT_IMPORTS = {
    "ceylon": "Use `ceylonai_next` package.",
}


def extract_code_blocks(filepath):
    """Extracts python code blocks from a markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex for fenced code blocks with python tag
    # Captures: (lang, content)
    pattern = r"```(python|py)\n(.*?)```"
    matches = re.finditer(pattern, content, re.DOTALL)

    blocks = []
    for m in matches:
        start_pos = m.start()
        # count newlines before start_pos to estimate line number
        line_num = content.count("\n", 0, start_pos) + 1
        blocks.append({"line": line_num, "content": m.group(2), "raw": m.group(0)})
    return blocks


def check_block(block, filepath):
    issues = []

    # 1. Check for deprecated APIs
    for api, msg in DEPRECATED_APIS.items():
        if api in block["content"]:
            issues.append(f"Deprecated API: `{api}` found. {msg}")

    # 2. Check for incorrect imports
    # Simple string check for now, can be made robust with AST
    for bad_imp, msg in INCORRECT_IMPORTS.items():
        # Look for "import ceylon" or "from ceylon"
        if re.search(f"import {bad_imp}\\b", block["content"]) or re.search(
            f"from {bad_imp}\\b", block["content"]
        ):
            issues.append(f"Incorrect Import: `{bad_imp}` found. {msg}")

    # 3. Check for numpy if not standard
    if "import numpy" in block["content"] or "from numpy" in block["content"]:
        issues.append(
            "Dependency Warning: `numpy` imported. Ensure it is listed in requirements."
        )

    # 4. Syntax Check
    try:
        ast.parse(block["content"])
    except SyntaxError as e:
        # Only report syntax errors if it looks like a complete script or substantial snippet
        # Many doc snippets are partial, so syntax errors are expected.
        # We can loosely report them as warnings?
        # For now, let's ignore syntax errors unless we are sure it's meant to be complete
        pass

    return issues


def main():
    print(f"Scanning docs in: {DOCS_DIR.absolute()}")
    md_files = []
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                md_files.append(Path(root) / file)

    print(f"Found {len(md_files)} markdown files.")

    results = {}

    for md_file in md_files:
        rel_path = md_file.relative_to(DOCS_DIR)
        blocks = extract_code_blocks(md_file)

        file_issues = []
        for block in blocks:
            block_issues = check_block(block, md_file)
            if block_issues:
                file_issues.append(
                    {
                        "line": block["line"],
                        "issues": block_issues,
                        "snippet": block["content"].strip()[:100] + "..."
                        if len(block["content"]) > 100
                        else block["content"].strip(),
                    }
                )

        if file_issues:
            results[str(rel_path)] = file_issues

    # Generate Report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# Python Documentation Code Analysis Report\n\n")
        f.write(
            f"**Date:** {os.environ.get('DATE', 'N/A')}\n"
        )  # Date not avail in env usually
        f.write(f"**Total Files Scanned:** {len(md_files)}\n")
        f.write(f"**Files with Issues:** {len(results)}\n\n")

        for filepath, issues in results.items():
            f.write(f"## {filepath}\n")
            for issue in issues:
                f.write(f"- **Line {issue['line']}**:\n")
                for i in issue["issues"]:
                    f.write(f"  - ⚠️ {i}\n")
                f.write(f"  - *Snippet*: `{issue['snippet'].replace('`', '')}`\n\n")

    print(f"Report generated: {REPORT_FILE}")


if __name__ == "__main__":
    main()
