#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module for AI-powered analysis of merge requests and commits using cursor-agent CLI."""

import json
from pathlib import Path
from typing import Optional, List, Union
from rich.console import Console
from rich.markdown import Markdown

from .config import config
from .mr_collector import MergeRequestSummary
from .commit_collector import CommitSummary
from .utils import run_command

console = Console()


class AIAnalyzer:
    """analyzer for summarizing merge requests and commits using AI."""

    def __init__(self, cursor_agent_path: Optional[str] = None, language: str = "en"):
        """initialize AI analyzer."""
        self.cursor_agent_path = cursor_agent_path or config.cursor_agent_path
        self.language = language
        self.is_available = self._check_availability()

    def _check_availability(self) -> bool:
        """check if cursor-agent is available."""
        if not self.cursor_agent_path:
            console.print(
                "[yellow]AI analysis not available: cursor-agent path not configured[/yellow]"
            )
            console.print(
                "[yellow]Set CURSOR_AGENT_PATH environment variable to enable AI features[/yellow]"
            )
            return False

        cursor_path = Path(self.cursor_agent_path)
        if not cursor_path.exists():
            console.print(
                f"[yellow]cursor-agent not found at: {self.cursor_agent_path}[/yellow]"
            )
            return False

        return True

    def _create_analysis_prompt(
        self,
        item: Union[MergeRequestSummary, CommitSummary],
        diff_content: Optional[str] = None,
        analysis_type: str = "summary",
    ) -> str:
        """create prompt for AI analysis."""
        if isinstance(item, MergeRequestSummary):
            base_info = f"""
# Merge Request Analysis

**MR !{item.iid}**: {item.title}
**Author**: {item.author}
**State**: {item.state}
**Created**: {item.created_at}
**Updated**: {item.updated_at}
**URL**: {item.web_url}

## Description
{item.description or 'No description provided.'}

## Statistics
- **Labels**: {', '.join(item.labels) if item.labels else 'None'}
- **Changes Count**: {item.changes_count or 'Unknown'}
"""
        else:
            base_info = f"""
# Commit Analysis

**Commit**: {item.short_sha}
**Author**: {item.author} <{item.author_email}>
**Authored**: {item.authored_date}
**Committed**: {item.committed_date}

## Commit Message
{item.message}

## Metadata
- **Parents**: {', '.join(item.parents) if item.parents else 'None'}
"""

        task = self._get_english_task(analysis_type)
        if self.language == "cn":
            task = self._get_chinese_task(analysis_type)

        prompt_sections = [base_info.strip(), task.strip()]

        if diff_content:
            prompt_sections.append(
                "\n".join(
                    [
                        "## Code Diff",
                        "```diff",
                        diff_content[:5000],
                        "```",
                        (
                            "(Diff truncated for brevity)"
                            if len(diff_content) > 5000
                            else ""
                        ),
                    ]
                ).strip()
            )

        return "\n\n".join(section for section in prompt_sections if section)

    def _get_english_task(self, analysis_type: str) -> str:
        """get English task for analysis."""
        if analysis_type == "summary":
            return """
Please provide a concise summary of this change:
1. What is the main purpose of this change?
2. Which key functionality or components are affected?
3. What is the overall impact on the project?

Keep the summary under 200 words.
"""
        if analysis_type == "impact":
            return """
Please analyze the impact of this change:
1. What areas of the codebase are affected?
2. What potential risks or regression areas exist?
3. Are there dependencies on specific environments or services?
4. What testing or validation is recommended before deployment?

Provide a detailed but concise analysis.
"""
        if analysis_type == "technical":
            return """
Please provide a technical analysis:
1. What implementation approach was used?
2. Are there notable design decisions?
3. How does this integrate with existing architecture?
4. Are there performance, security, or compliance considerations?

Focus on technical depth.
"""
        return "Please analyze this change and provide actionable insights."

    def _get_chinese_task(self, analysis_type: str) -> str:
        """get Chinese task for analysis."""
        if analysis_type == "summary":
            return """
请用中文提供此变更的简要总结：
1. 此变更的主要目的是什么？
2. 受影响的关键功能或组件有哪些？
3. 对项目的整体影响是什么？

请保持总结在 200 字以内，使用左对齐格式。
"""
        if analysis_type == "impact":
            return """
请用中文分析此变更的影响：
1. 代码库中哪些区域受到影响？
2. 有哪些潜在的风险或回归点？
3. 是否依赖特定环境或服务？
4. 建议进行哪些测试或验证？

请提供详细但简洁的分析，使用左对齐格式。
"""
        if analysis_type == "technical":
            return """
请用中文提供技术分析：
1. 使用了什么实现方案？
2. 有哪些值得注意的设计决策？
3. 这如何融入现有架构？
4. 是否存在性能、安全或合规方面的考虑？

请专注于技术深度，使用左对齐格式。
"""
        return "请用中文分析此变更并提供可执行的建议，使用左对齐格式。"

    def analyze(
        self,
        item: Union[MergeRequestSummary, CommitSummary],
        include_diff: bool = True,
        analysis_type: str = "summary",
        diff_provider: Optional[callable] = None,
    ) -> Optional[str]:
        """analyze a merge request or commit using AI."""
        if not self.is_available:
            console.print("[red]AI analysis not available[/red]")
            return None

        console.print("[cyan]Analyzing with AI...[/cyan]")

        diff_content = None
        if include_diff and diff_provider:
            try:
                diff_content = diff_provider(item)
            except Exception as error:
                console.print(f"[yellow]failed to fetch diff: {error}[/yellow]")

        prompt = self._create_analysis_prompt(item, diff_content, analysis_type)

        try:
            command = [
                self.cursor_agent_path,
                "--print",
                "--output-format",
                "text",
                "agent",
                prompt,
            ]

            _, stdout, stderr = run_command(command, check=False)

            if stderr:
                console.print(f"[yellow]Warning: {stderr}[/yellow]")

            if stdout:
                return stdout.strip()

            console.print("[red]AI analysis produced no output[/red]")
            return None

        except Exception as error:
            console.print(f"[red]Error during AI analysis: {error}[/red]")
            return None

    def batch_analyze(
        self,
        items: List[Union[MergeRequestSummary, CommitSummary]],
        include_diff: bool = False,
        analysis_type: str = "summary",
        diff_provider: Optional[callable] = None,
    ) -> List[tuple[Union[MergeRequestSummary, CommitSummary], Optional[str]]]:
        """analyze multiple items in batch."""
        if not self.is_available:
            console.print("[red]AI analysis not available[/red]")
            return [(item, None) for item in items]

        results = []
        total = len(items)

        for index, item in enumerate(items, 1):
            console.print(f"[cyan]Analyzing {index}/{total}...[/cyan]")
            analysis = self.analyze(
                item,
                include_diff=include_diff,
                analysis_type=analysis_type,
                diff_provider=diff_provider,
            )
            results.append((item, analysis))

        return results

    def display_analysis(
        self, item: Union[MergeRequestSummary, CommitSummary], analysis: str
    ) -> None:
        """display analysis result in a formatted way."""
        if isinstance(item, MergeRequestSummary):
            title = f"AI Analysis: MR !{item.iid} - {item.title}"
        else:
            title = f"AI Analysis: Commit {item.short_sha}"

        console.print("\n" + "=" * 80)
        console.print(f"[bold cyan]{title}[/bold cyan]")
        console.print("=" * 80 + "\n")

        try:
            console.print(Markdown(analysis))
        except Exception:
            console.print(analysis)

        console.print("\n")

    def generate_summary_report(
        self,
        analyzed_items: List[
            tuple[Union[MergeRequestSummary, CommitSummary], Optional[str]]
        ],
        query: Optional[str] = None,
    ) -> str:
        """generate a summary report from analyzed items."""
        lines = ["# GitLab Merge Request & Commit Analysis Report", ""]

        if query:
            lines.append(f"**Search Query**: {query}")
            lines.append("")

        lines.append(f"**Total Items Analyzed**: {len(analyzed_items)}")
        lines.append("")
        lines.append("---")
        lines.append("")

        for index, (item, analysis) in enumerate(analyzed_items, 1):
            if isinstance(item, MergeRequestSummary):
                lines.append(f"## {index}. MR !{item.iid}: {item.title}")
                lines.append(f"- **Author**: {item.author}")
                lines.append(f"- **State**: {item.state}")
                lines.append(f"- **URL**: {item.web_url}")
            else:
                title = item.message.split("\n")[0]
                lines.append(f"## {index}. Commit {item.short_sha}: {title}")
                lines.append(f"- **Author**: {item.author}")
                lines.append(f"- **Authored**: {item.authored_date}")
                lines.append(f"- **Committed**: {item.committed_date}")

            lines.append("")

            if analysis:
                lines.append("### Analysis")
                lines.append(analysis)
            else:
                lines.append("*No analysis available*")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)
