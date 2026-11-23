#!/usr/bin/env python3
"""Build reading metadata from content-index.json without changing source prose.

Run normally to update registered documents and the marked README index. Use
--check to validate the registry and report generated content that is stale.
Only the Python standard library is required.
"""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import sys
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
INDEX_BEGIN = "<!-- BEGIN GENERATED RESEARCH INDEX -->"
INDEX_END = "<!-- END GENERATED RESEARCH INDEX -->"
SUMMARY_BEGIN = "<!-- BEGIN GENERATED READING SUMMARY -->"
SUMMARY_END = "<!-- END GENERATED READING SUMMARY -->"
FRONTMATTER_FIELDS = (
    "document_id", "title_zh", "title_en", "language", "kind",
    "evidence_as_of", "indexed_on",
)
DATED_TAGS = {"FACT", "AUTHOR_REPORT", "LOCAL_RESULT"}
PREFIX_PATTERN = re.compile(r"[A-Z0-9]+\Z")
ID_PATTERN = re.compile(r"[A-Z0-9]+-[0-9]{3}\Z")
H1_PATTERN = re.compile(r"^# ([^\r\n]+)", re.MULTILINE)


class IndexError(ValueError):
    """An invalid registry or a malformed generated region."""


def read_utf8(path: Path) -> str:
    # read_text() performs universal-newline conversion; source prose must not.
    return path.read_bytes().decode("utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise IndexError(message)


def string(value: object, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{label}: expected a nonempty string")
    require(not any(c in value for c in "\r\n\x00"), f"{label}: must be a single line")
    return value


def strings(value: object, label: str, *, nonempty: bool = True) -> list[str]:
    require(isinstance(value, list), f"{label}: expected an array")
    require(bool(value) or not nonempty, f"{label}: must not be empty")
    for item in value:
        string(item, label)
    require(len(value) == len(set(value)), f"{label}: duplicate values")
    return value


def valid_date(value: object, label: str, *, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is not None,
            f"{label}: expected YYYY-MM-DD" + (" or null" if nullable else ""))
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise IndexError(f"{label}: invalid calendar date {value!r}") from exc


def document_path(value: object, root: Path) -> Path:
    path = string(value, "document.path")
    parts = path.split("/")
    require(not PurePosixPath(path).is_absolute() and all(p not in {"", ".", ".."} for p in parts),
            f"{path}: use a canonical relative path without dot segments")
    require(not any(c in path for c in "\\<>\t") and not re.match(r"^[A-Za-z]:", path),
            f"{path}: unsafe relative path")
    require(path.endswith(".md"), f"{path}: registered documents must be Markdown files")
    target = root.joinpath(*parts)
    require(target.resolve().is_relative_to(root.resolve()), f"{path}: path escapes the repository")
    require(target.is_file(), f"{path}: document does not exist")
    return target


def frontmatter_fields(doc: dict) -> tuple[str, ...]:
    if "session_id" in doc:
        return (FRONTMATTER_FIELDS[0], "session_id", *FRONTMATTER_FIELDS[1:])
    return FRONTMATTER_FIELDS


def glob_paths(patterns: object, root: Path, label: str, *, nonempty: bool) -> set[str]:
    """Expand canonical, repository-relative globs into safe Markdown paths."""
    result = set()
    for pattern in strings(patterns, label, nonempty=nonempty):
        parts = pattern.split("/")
        require(not PurePosixPath(pattern).is_absolute()
                and all(part not in {"", ".", ".."} for part in parts),
                f"{label}: glob must be a canonical relative path: {pattern!r}")
        require(not any(c in pattern for c in "\\<>\t")
                and not re.match(r"^[A-Za-z]:", pattern),
                f"{label}: unsafe glob {pattern!r}")
        require(all("**" not in part or part == "**" for part in parts),
                f"{label}: ** must occupy an entire path component: {pattern!r}")
        try:
            for target in root.glob(pattern):
                require(target.resolve().is_relative_to(root.resolve()),
                        f"{label}: glob match escapes the repository: {target}")
                if target.is_file() and target.suffix == ".md":
                    relative = target.relative_to(root).as_posix()
                    document_path(relative, root)
                    result.add(relative)
        except ValueError as exc:
            raise IndexError(f"{label}: invalid glob {pattern!r}: {exc}") from exc
    return result


def strip_generated(text: str) -> str:
    """Remove only this builder's frontmatter and reading-summary insertion.

    Frontmatter is recognized by its exact field order and PREFIX-NNN ID,
    optionally with an equal session_id immediately after document_id.
    Unrelated YAML frontmatter is left untouched. The summary insertion owns
    precisely its two leading LF characters and nothing after the end marker,
    so the original H1, line endings, whitespace, and remaining prose survive.
    """
    if text.startswith("---\n"):
        end = text.find("\n---\n\n", 4)
        if end != -1:
            lines = text[4:end].split("\n")
            keys = [line.partition(":")[0] for line in lines]
            session_fields = [FRONTMATTER_FIELDS[0], "session_id", *FRONTMATTER_FIELDS[1:]]
            if keys in (list(FRONTMATTER_FIELDS), session_fields):
                try:
                    values = {key: json.loads(line.partition(":")[2].strip())
                              for key, line in zip(keys, lines)}
                except json.JSONDecodeError as exc:
                    raise IndexError("Malformed generated frontmatter") from exc
                if isinstance(values["document_id"], str) and ID_PATTERN.fullmatch(values["document_id"]):
                    require("session_id" not in values or values["session_id"] == values["document_id"],
                            "Generated session_id must equal document_id")
                    text = text[end + len("\n---\n\n"):]

    begin_count, end_count = text.count(SUMMARY_BEGIN), text.count(SUMMARY_END)
    require((begin_count, end_count) in {(0, 0), (1, 1)},
            "Reading summary: missing or repeated generated markers")
    if begin_count:
        start = text.index(SUMMARY_BEGIN)
        end = text.index(SUMMARY_END)
        require(start < end and start >= 2 and text[start - 2:start] == "\n\n",
                "Reading summary: malformed generated region")
        text = text[:start - 2] + text[end + len(SUMMARY_END):]
    return text


def validate_registry(registry: object, root: Path) -> dict[str, str]:
    """Validate metadata and paths; return original text keyed by document ID."""
    require(isinstance(registry, dict), "Registry must be a JSON object")
    require(type(registry.get("schema_version")) is int and registry["schema_version"] == 1,
            "schema_version must be 1")
    valid_date(registry.get("updated_on"), "updated_on")
    prefix = string(registry.get("id_prefix"), "id_prefix")
    require(PREFIX_PATTERN.fullmatch(prefix) is not None,
            "id_prefix must contain uppercase ASCII letters and digits only")
    prefixed_id_pattern = re.compile(re.escape(prefix) + r"-[0-9]{3}\Z")
    primary_paths = glob_paths(registry.get("document_globs"), root, "document_globs", nonempty=True)
    excluded_paths = glob_paths(registry.get("exclude_globs", []), root, "exclude_globs", nonempty=False)
    primary_paths -= excluded_paths

    categories = registry.get("categories")
    require(isinstance(categories, list), "categories must be an array")
    category_ids = []
    for category in categories:
        require(isinstance(category, dict), "Each category must be an object")
        category_ids.append(string(category.get("id"), "category.id"))
        string(category.get("title_zh"), "category.title_zh")
        string(category.get("title_en"), "category.title_en")
    require(len(category_ids) == len(set(category_ids)), "Duplicate category IDs")

    kinds = registry.get("kinds")
    require(isinstance(kinds, dict), "kinds must be an object")
    for kind, labels in kinds.items():
        string(kind, "kind")
        require(isinstance(labels, dict), f"kind {kind}: expected an object")
        string(labels.get("title_zh"), f"kind {kind}.title_zh")
        string(labels.get("title_en"), f"kind {kind}.title_en")

    tags = registry.get("evidence_tags")
    require(isinstance(tags, dict), "evidence_tags must be an object")
    for tag, labels in tags.items():
        require(re.fullmatch(r"[A-Z][A-Z0-9_]*", tag) is not None, f"Invalid evidence tag {tag!r}")
        require(isinstance(labels, dict), f"tag {tag}: expected an object")
        string(labels.get("title_zh"), f"tag {tag}.title_zh")
        string(labels.get("description_zh"), f"tag {tag}.description_zh")

    documents = registry.get("documents")
    require(isinstance(documents, list), "documents must be an array")
    ids, paths, originals = set(), set(), {}
    for doc in documents:
        require(isinstance(doc, dict), "Each document must be an object")
        doc_id = string(doc.get("document_id"), "document_id")
        require(prefixed_id_pattern.fullmatch(doc_id) is not None, f"{doc_id}: expected {prefix}-NNN")
        if "session_id" in doc:
            require(doc["session_id"] == doc_id, f"{doc_id}: session_id must equal document_id")
        require(doc_id not in ids, f"Duplicate document ID: {doc_id}")
        ids.add(doc_id)
        target = document_path(doc.get("path"), root)
        require(doc["path"] not in paths, f"Duplicate document path: {doc['path']}")
        paths.add(doc["path"])
        for field in ("title_zh", "title_en", "language", "question_zh", "scope_zh"):
            string(doc.get(field), f"{doc_id}.{field}")
        require(doc.get("kind") in kinds, f"{doc_id}: unknown kind")
        require(doc.get("category") in category_ids, f"{doc_id}: unknown category")
        valid_date(doc.get("evidence_as_of"), f"{doc_id}.evidence_as_of", nullable=True)
        valid_date(doc.get("indexed_on"), f"{doc_id}.indexed_on")
        require(("content_date" in doc) == ("content_date_kind" in doc),
                f"{doc_id}: content_date and content_date_kind must be provided together")
        if "content_date" in doc:
            valid_date(doc["content_date"], f"{doc_id}.content_date")
            require(doc["content_date_kind"] in {"discussion", "archive", "record"},
                    f"{doc_id}: content_date_kind must be discussion, archive, or record")
        topics_zh = strings(doc.get("topics_zh"), f"{doc_id}.topics_zh")
        topics_en = strings(doc.get("topics_en"), f"{doc_id}.topics_en")
        require(len(topics_zh) == len(topics_en), f"{doc_id}: bilingual topic arrays must correspond")
        summary = doc.get("reading_summary")
        require(isinstance(summary, list) and 2 <= len(summary) <= 3,
                f"{doc_id}.reading_summary: expected 2 or 3 claims")
        for claim in summary:
            require(isinstance(claim, dict), f"{doc_id}: each summary claim must be an object")
            require(claim.get("tag") in tags, f"{doc_id}: unknown summary evidence tag")
            string(claim.get("text_zh"), f"{doc_id}.reading_summary.text_zh")
        strings(doc.get("related_ids"), f"{doc_id}.related_ids", nonempty=False)

        source = strip_generated(read_utf8(target))
        require(not source.startswith(("---\n", "---\r\n")),
                f"{doc_id}: unrelated frontmatter requires manual integration")
        h1 = H1_PATTERN.search(source)
        require(h1 is not None and h1.group(1).strip() == doc["title_zh"],
                f"{doc_id}: original H1 must equal title_zh")
        originals[doc_id] = source

    require(not primary_paths - paths,
            "Unregistered primary documents: " + ", ".join(sorted(primary_paths - paths)))
    require(not paths - primary_paths,
            "Registered documents outside configured document_globs or explicitly excluded: "
            + ", ".join(sorted(paths - primary_paths)))

    for doc in documents:
        for related in doc["related_ids"]:
            require(related in ids, f"{doc['document_id']}: unknown related ID {related}")
            require(related != doc["document_id"], f"{related}: self relation is not allowed")
    routes = registry.get("reading_routes")
    require(isinstance(routes, list), "reading_routes must be an array")
    for route in routes:
        require(isinstance(route, dict), "Each reading route must be an object")
        string(route.get("title_zh"), "reading route.title_zh")
        string(route.get("title_en"), "reading route.title_en")
        for doc_id in strings(route.get("document_ids"), "reading route.document_ids"):
            require(doc_id in ids, f"Reading route references unknown ID {doc_id}")
    return originals


def label(text: str) -> str:
    """Escape link/table labels while preserving readable bilingual text."""
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]").replace("|", "\\|")


def link(title: str, path: str) -> str:
    return f"[{label(title)}]({quote(path, safe='/._~-')})"


def dates_label(doc: dict) -> str:
    if "content_date" in doc:
        kinds = {"discussion": "讨论", "archive": "存档", "record": "记录"}
        content = f"{kinds[doc['content_date_kind']]} {doc['content_date']}"
        evidence = (f"证据截至 {doc['evidence_as_of']}" if doc["evidence_as_of"]
                    else "证据截止未注明")
        return content + "；" + evidence
    return doc["evidence_as_of"] or "未注明 · Not specified"


def render_document(doc: dict, source: str, documents: dict[str, dict]) -> str:
    frontmatter = ["---"]
    for field in frontmatter_fields(doc):
        frontmatter.append(f"{field}: {json.dumps(doc[field], ensure_ascii=False)}")
    frontmatter.extend(["---", "", ""])
    summary = [SUMMARY_BEGIN, "## 阅读摘要 · Reading Summary", "",
               f"**核心问题：** {doc['question_zh']}", ""]
    for claim in doc["reading_summary"]:
        annotation = f"[{claim['tag']}]"
        if claim["tag"] in DATED_TAGS and doc["evidence_as_of"] is not None:
            annotation += f" [AS_OF:{doc['evidence_as_of']}]"
        summary.append(f"- {annotation} {claim['text_zh']}")
    summary.extend(["", f"**适用边界：** {doc['scope_zh']}", ""])
    directory = posixpath.dirname(doc["path"]) or "."
    if doc["related_ids"]:
        related = [link(f"{related_id} {documents[related_id]['title_zh']}",
                        posixpath.relpath(documents[related_id]["path"], directory))
                   for related_id in doc["related_ids"]]
        summary.extend(["**相关文档：** " + "；".join(related), ""])
    summary.extend([link("返回总目录 · Content Index", posixpath.relpath("README.md", directory)),
                    SUMMARY_END])
    h1 = H1_PATTERN.search(source)
    insertion = "\n\n" + "\n".join(summary)
    body = source[:h1.end()] + insertion + source[h1.end():]
    result = "\n".join(frontmatter) + body
    require(strip_generated(result) == source, f"{doc['document_id']}: generated content changed original prose")
    return result


def render_index(registry: dict) -> str:
    documents = {doc["document_id"]: doc for doc in registry["documents"]}
    lines = [INDEX_BEGIN]
    if not documents:
        lines.extend(["## 内容索引 · Content Index", "",
                      "暂无已归档主题。 · No topics have been archived yet.", "", INDEX_END])
        return "\n".join(lines)
    if registry["reading_routes"]:
        lines.extend(["## 推荐阅读路径 · Suggested Reading Routes", ""])
        for route in registry["reading_routes"]:
            lines.extend([f"### {route['title_zh']} · {route['title_en']}", ""])
            for number, doc_id in enumerate(route["document_ids"], 1):
                doc = documents[doc_id]
                lines.append(f"{number}. {link(doc_id + ' ' + doc['title_zh'], doc['path'])}")
            lines.append("")
    lines.extend(["## 内容索引 · Content Index", ""])
    for category in registry["categories"]:
        if not any(doc["category"] == category["id"] for doc in registry["documents"]):
            continue
        lines.extend([f"### {category['title_zh']} · {category['title_en']}", "",
                      "| ID | 中文文档 | English Title | 类型 · Type | 日期与口径 · Dates |",
                      "|---|---|---|---|---|"])
        for doc in registry["documents"]:
            if doc["category"] != category["id"]:
                continue
            kind = registry["kinds"][doc["kind"]]
            kind_label = label(kind["title_zh"] + " · " + kind["title_en"])
            evidence_date = dates_label(doc)
            lines.append(f"| {doc['document_id']} | {link(doc['title_zh'], doc['path'])} | "
                         f"{label(doc['title_en'])} | {kind_label} | {evidence_date} |")
        lines.append("")
    lines.append(INDEX_END)
    return "\n".join(lines)


def replace_index(readme: str, generated: str) -> str:
    require(readme.count(INDEX_BEGIN) == 1 and readme.count(INDEX_END) == 1,
            "README must contain exactly one pair of generated research-index markers")
    start, end = readme.index(INDEX_BEGIN), readme.index(INDEX_END)
    require(start < end, "README generated index markers are reversed")
    return readme[:start] + generated + readme[end + len(INDEX_END):]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate and detect stale generated content without writing")
    args = parser.parse_args()
    try:
        registry = json.loads(read_utf8(ROOT / "content-index.json"))
        originals = validate_registry(registry, ROOT)
        documents = {doc["document_id"]: doc for doc in registry["documents"]}
        # Prepare and validate every output before the first write.
        outputs = {ROOT / doc["path"]: render_document(doc, originals[doc["document_id"]], documents)
                   for doc in registry["documents"]}
        readme_path = ROOT / "README.md"
        outputs[readme_path] = replace_index(read_utf8(readme_path), render_index(registry))
        stale = [path for path, content in outputs.items() if read_utf8(path) != content]
        if args.check:
            if stale:
                print("Generated content is stale:")
                for path in stale:
                    print(f"  {path.relative_to(ROOT).as_posix()}")
                return 1
            print(f"Checked {len(documents)} documents and README: all generated content is current.")
        else:
            for path in stale:
                path.write_bytes(outputs[path].encode("utf-8"))
            print(f"Validated {len(documents)} documents; updated {len(stale)} files.")
        return 0
    except (IndexError, OSError, UnicodeError, json.JSONDecodeError, TypeError, KeyError) as exc:
        print(f"Reading index error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
