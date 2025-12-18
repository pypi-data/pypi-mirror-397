#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""smart search analyzer for extracting search keywords using AI."""

import json
import re
import tempfile
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from .config import config
from .utils import run_command

console = Console()


class SmartSearchAnalyzer:
    """extract optimal search keywords from user query."""

    def __init__(self, cursor_agent_path: Optional[str] = None):
        self.cursor_agent_path = cursor_agent_path or config.cursor_agent_path
        self.is_available = self._check_availability()

    def _check_availability(self) -> bool:
        if not self.cursor_agent_path:
            return False
        cursor_path = Path(self.cursor_agent_path)
        if not cursor_path.exists():
            return False
        return True

    def _create_keyword_extraction_prompt(self, user_query: str) -> str:
        prompt = """
# Search Query Analysis Task

## User Query
"{query}"

## Task
Analyze the user's search query and extract the most effective search keywords for finding relevant GitLab merge requests and commits.

## Requirements
1. Extract 5-10 high-quality search keywords/phrases
2. Prioritize keywords by relevance and discriminative power
3. Include different types of keywords:
   - technical terms (functions, APIs, technologies)
   - action words (fix, add, update, refactor, etc.)
   - domain-specific terms
   - author names (if mentioned)
   - file types or paths (if relevant)

## Output Format
Provide ONLY a JSON array of keywords, ordered by priority:

```json
[
  "keyword1",
  "keyword2"
]
```

Now analyze the user query and provide the keyword array:
""".format(query=user_query)
        return prompt

    def extract_search_keywords(self, user_query: str) -> List[str]:
        if not self.is_available:
            return self._fallback_keyword_extraction(user_query)

        console.print("[cyan]Analyzing search query with AI...[/cyan]")
        prompt = self._create_keyword_extraction_prompt(user_query)

        prompt_file = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                f.write(prompt)
                prompt_file = f.name

            command = [self.cursor_agent_path, "--file", prompt_file]
            _, stdout, stderr = run_command(command, check=False)

            if prompt_file:
                Path(prompt_file).unlink(missing_ok=True)

            if stderr:
                console.print("[yellow]Warning: {0}[/yellow]".format(stderr))

            if stdout:
                keywords = self._parse_keywords_response(stdout.strip())
                if keywords:
                    console.print(
                        "[green]✓ Extracted {0} keywords[/green]".format(len(keywords))
                    )
                    return keywords

            console.print("[yellow]AI keyword extraction failed, using fallback[/yellow]")
            return self._fallback_keyword_extraction(user_query)

        except Exception as exc:
            if prompt_file:
                try:
                    Path(prompt_file).unlink(missing_ok=True)
                except Exception:
                    pass
            console.print(
                "[yellow]AI keyword extraction error, using fallback: {0}[/yellow]".format(
                    exc
                )
            )
            return self._fallback_keyword_extraction(user_query)

    def _parse_keywords_response(self, response: str) -> List[str]:
        try:
            json_pattern = r"\[[\s\S]*?\]"
            matches = re.findall(json_pattern, response)
            for match in matches:
                try:
                    keywords = json.loads(match)
                except json.JSONDecodeError:
                    continue

                if not isinstance(keywords, list):
                    continue

                cleaned: List[str] = []
                for item in keywords:
                    if not isinstance(item, str):
                        continue
                    value = item.strip()
                    if not value:
                        continue
                    cleaned.append(value)

                if cleaned:
                    if len(cleaned) > 10:
                        return cleaned[:10]
                    return cleaned

            # fallback: extract lines that look like keywords
            lines = response.split("\n")
            keywords_text: List[str] = []
            for line in lines:
                line_value = line.strip()
                if not line_value:
                    continue
                if line_value.startswith("#"):
                    continue
                if line_value.startswith("```"):
                    continue
                cleaned_line = re.sub(r'["\'\[\],]', "", line_value).strip()
                if len(cleaned_line) > 1:
                    keywords_text.append(cleaned_line)

            if len(keywords_text) > 10:
                return keywords_text[:10]
            return keywords_text

        except Exception:
            return []

    def _fallback_keyword_extraction(self, user_query: str) -> List[str]:
        query = user_query.lower().strip()
        words = re.findall(r"\b\w+\b", query)

        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
        }

        keywords: List[str] = []
        for word in words:
            if len(word) <= 2:
                continue
            if word in stop_words:
                continue
            keywords.append(word)

        # add 2-word phrases
        phrases: List[str] = []
        for idx in range(len(words) - 1):
            phrase = " ".join(words[idx : idx + 2])
            if len(phrase) > 4:
                phrases.append(phrase)

        priority_patterns = [
            r"\b(fix|bug|error|issue)\b",
            r"\b(add|new|create|implement)\b",
            r"\b(update|modify|change|edit)\b",
            r"\b(refactor|cleanup|optimize)\b",
            r"\b(api|endpoint|service|function)\b",
            r"\b(database|db|sql|query)\b",
            r"\b(auth|authentication|login|security)\b",
            r"\b(test|testing|unit|integration)\b",
        ]

        priority_keywords: List[str] = []
        for pattern in priority_patterns:
            matches = re.findall(pattern, query)
            for value in matches:
                priority_keywords.append(value)

        all_keywords = []
        all_keywords.extend(priority_keywords)
        all_keywords.extend(keywords)
        all_keywords.extend(phrases)

        seen = set()
        result: List[str] = []
        for kw in all_keywords:
            if not kw:
                continue
            if kw in seen:
                continue
            seen.add(kw)
            result.append(kw)

        if len(result) > 10:
            return result[:10]
        return result


