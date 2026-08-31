#!/usr/bin/env python3
"""Validate repository structure without third-party dependencies."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote


TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py"}
REQUIRED_CASE_FIELDS = {
    "case_id",
    "question",
    "question_category",
    "question_subtype",
    "success_criterion",
    "target_event",
    "event_chain_stage",
    "chart_time",
    "system",
    "input_file",
    "yongshen",
    "analysis_file",
    "prediction_ledger_file",
    "qualitative_rating",
    "timing_windows",
    "prediction_confidence",
    "invalidation_conditions",
    "outcome_file",
    "review_file",
    "error_types",
    "privacy",
    "created_at",
    "outcome_recorded_at",
    "skill_version",
}


class Validator:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.errors: list[str] = []
        self.files_checked: set[Path] = set()
        self.scenario_files = 0
        self.scenarios = 0
        self.module_routes = 0

    def error(self, message: str) -> None:
        self.errors.append(message)

    def read(self, path: Path) -> str:
        try:
            data = path.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeError) as exc:
            self.error(f"cannot read UTF-8: {path}: {exc}")
            return ""
        self.files_checked.add(path.resolve())
        return data

    def validate_text_files(self) -> None:
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = self.read(path)
            relative = path.relative_to(self.root)
            if "[TO" + "DO:" in text:
                self.error(f"unfinished TODO placeholder: {relative}")
            for line_number, line in enumerate(text.splitlines(), start=1):
                if re.match(r"^(<<<<<<<|=======|>>>>>>>)", line):
                    self.error(f"merge conflict marker: {relative}:{line_number}")
                if line.endswith((" ", "\t")):
                    self.error(f"trailing whitespace: {relative}:{line_number}")
            if path.suffix.lower() != ".md":
                continue
            for match in link_pattern.finditer(text):
                target = match.group(1).strip()
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                if target.startswith("<") and target.endswith(">"):
                    target = target[1:-1]
                target = unquote(target.split("#", 1)[0])
                if not target:
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.exists():
                    self.error(f"broken local link: {relative} -> {target}")

    def validate_skill_entrypoint(self) -> None:
        path = self.root / "SKILL.md"
        text = self.read(path)
        match = re.match(r"\A---\r?\n(.*?)\r?\n---", text, re.DOTALL)
        if not match:
            self.error("SKILL.md has invalid or missing frontmatter")
            return
        frontmatter = match.group(1)
        name_match = re.search(r"(?m)^name:\s*([^\s]+)\s*$", frontmatter)
        description_match = re.search(r"(?m)^description:\s*(.+?)\s*$", frontmatter)
        if not name_match:
            self.error("SKILL.md frontmatter is missing name")
        else:
            name = name_match.group(1)
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
                self.error(f"invalid skill name: {name}")
            if name != self.root.name:
                self.error(f"skill name {name} does not match folder {self.root.name}")
        if not description_match or not description_match.group(1).strip():
            self.error("SKILL.md frontmatter is missing description")

        routes = sorted(set(re.findall(r"\((modules/[^)]+/README\.md)\)", text)))
        self.module_routes = len(routes)
        if len(routes) < 8:
            self.error(f"expected at least 8 module routes, found {len(routes)}")
        for route in routes:
            if not (self.root / route).is_file():
                self.error(f"missing routed module: {route}")

    def validate_scenarios(self) -> None:
        ids: dict[str, Path] = {}
        counts: dict[str, int] = {}
        scenario_pattern = re.compile(
            r"(?ms)^\s*-\s+test_id:\s*\"([^\"]+)\"(.*?)(?=^\s*-\s+test_id:|\Z)"
        )
        for path in sorted((self.root / "tests").glob("*-scenarios.yaml")):
            text = self.read(path)
            self.scenario_files += 1
            if not re.search(r"(?m)^schema_version:\s*\"[^\"]+\"", text):
                self.error(f"missing schema_version: tests/{path.name}")
            if not re.search(r"(?m)^purpose:\s*\"[^\"]+\"", text):
                self.error(f"missing purpose: tests/{path.name}")
            matches = list(scenario_pattern.finditer(text))
            counts[path.name] = len(matches)
            self.scenarios += len(matches)
            if not matches:
                self.error(f"no scenarios found: tests/{path.name}")
            for match in matches:
                test_id, block = match.group(1), match.group(2)
                if test_id in ids:
                    self.error(
                        f"duplicate test_id {test_id}: {ids[test_id].name}, {path.name}"
                    )
                ids[test_id] = path
                if not re.search(r"(?m)^\s+situation:\s*\"[^\"]+\"", block):
                    self.error(f"missing situation for {test_id} in {path.name}")
                if not re.search(r"(?m)^\s+expect:\s*$", block):
                    self.error(f"missing expect list for {test_id} in {path.name}")
                if not re.search(r"(?m)^\s+-\s+\"[^\"]+\"", block):
                    self.error(f"empty expect list for {test_id} in {path.name}")

        baseline_path = self.root / "tests" / "coverage-baseline.yaml"
        baseline = self.read(baseline_path)
        total_match = re.search(r"(?m)^minimum_total:\s*(\d+)\s*$", baseline)
        if not total_match:
            self.error("coverage baseline is missing minimum_total")
        elif self.scenarios < int(total_match.group(1)):
            self.error(
                f"scenario total {self.scenarios} is below baseline {total_match.group(1)}"
            )
        expected = {
            name: int(value)
            for name, value in re.findall(
                r"(?m)^\s{2}([^:#\s]+-scenarios\.yaml):\s*(\d+)\s*$", baseline
            )
        }
        for name, minimum in expected.items():
            actual = counts.get(name)
            if actual is None:
                self.error(f"baseline scenario file is missing: tests/{name}")
            elif actual < minimum:
                self.error(f"{name} has {actual} scenarios; baseline requires {minimum}")
        extra = sorted(set(counts) - set(expected))
        if extra:
            self.error(f"scenario files missing from coverage baseline: {', '.join(extra)}")

    def validate_case_schema(self) -> None:
        template_path = self.root / "cases" / "case-template.yaml"
        template = self.read(template_path)
        fields = set(re.findall(r"(?m)^([a-z_]+):", template))
        missing = sorted(REQUIRED_CASE_FIELDS - fields)
        if missing:
            self.error(f"case template missing fields: {', '.join(missing)}")

        readme = self.read(self.root / "README.md")
        version_match = re.search(r"当前版本：V([^\s]+)", readme)
        case_version_match = re.search(r'(?m)^skill_version:\s*\"([^\"]+)\"', template)
        if not version_match or not case_version_match:
            self.error("cannot compare README and case template versions")
        elif not case_version_match.group(1).startswith(version_match.group(1)):
            self.error(
                f"case version {case_version_match.group(1)} does not match "
                f"README version {version_match.group(1)}"
            )

        registry = self.read(self.root / "tests" / "regression-cases.yaml")
        if not re.search(r"(?m)^schema_version:\s*\"0\.8\"", registry):
            self.error("regression case registry schema_version must be 0.8")
        if not re.search(r"(?m)^tests:\s*\[\]\s*$", registry):
            return
        if not re.search(r"(?m)^accuracy_claim_allowed:\s*false\s*$", registry):
            self.error("empty real-case registry must disable accuracy claims")

    def validate_v12_contract(self) -> None:
        required = [
            "rules/qualitative-rating.md",
            "rules/future-event-tree.md",
            "rules/timing.md",
            "rules/multi-chart-comparison.md",
            "rules/strategy-engine.md",
            "rules/event-chain-templates.md",
            "rules/rule-confidence.md",
            "cases/prediction-ledger.md",
        ]
        for relative in required:
            if not (self.root / relative).is_file():
                self.error(f"missing V1.2 authority file: {relative}")

        version = self.read(self.root / "VERSION").strip()
        if version != "1.2.0":
            self.error(f"VERSION must be 1.2.0, found {version!r}")

        standard = self.read(self.root / "output" / "standard-analysis.md")
        expected_headings = [
            "# 一、问题、核验与取用",
            "# 二、整体局势",
            "# 三、核心人物 / 事情状态",
            "# 四、关键关系与动力",
            "# 五、有利因素",
            "# 六、不利因素",
            "# 七、未来趋势",
            "# 八、关键转折条件",
            "# 九、应期与时间窗口",
            "# 十、趋吉避凶策略",
            "# 十一、风险与不确定性",
            "# 十二、大白话结论",
        ]
        positions = [standard.find(item) for item in expected_headings]
        if any(position < 0 for position in positions):
            self.error("standard output is missing one or more locked V1.2 headings")
        elif positions != sorted(positions):
            self.error("standard output V1.2 headings are out of order")
        rating_position = standard.find("【定性评价】")
        if rating_position < 0 or (positions and rating_position > positions[0]):
            self.error("qualitative rating must precede the first formal heading")

        rating = self.read(self.root / "rules" / "qualitative-rating.md")
        for level in ("大吉", "吉", "小吉", "平偏吉", "平", "平偏凶", "小凶", "凶", "大凶"):
            if level not in rating:
                self.error(f"qualitative rating is missing level: {level}")

        timing = self.read(self.root / "rules" / "timing.md")
        for phrase in ("目标事件 E", "连续触宫", "最多三个", "置信度", "现实验证信号", "失效条件"):
            if phrase not in timing:
                self.error(f"timing V1 is missing required concept: {phrase}")
        for deprecated in ("当前仍未建立经过案例回归的具体算法", "应期算法未来启用前"):
            if deprecated in timing:
                self.error(f"deprecated V1.1 timing rule remains: {deprecated}")

    def run(self) -> int:
        if not self.root.is_dir():
            print(f"ERROR: skill directory does not exist: {self.root}", file=sys.stderr)
            return 2
        self.validate_text_files()
        self.validate_skill_entrypoint()
        self.validate_scenarios()
        self.validate_case_schema()
        self.validate_v12_contract()
        if self.errors:
            print(f"Skill validation failed with {len(self.errors)} error(s):")
            for error in self.errors:
                print(f"- {error}")
            return 1
        print("Skill validation passed.")
        print(f"Text files checked: {len(self.files_checked)}")
        print(f"Routed modules: {self.module_routes}")
        print(f"Scenario files: {self.scenario_files}")
        print(f"Synthetic scenarios: {self.scenarios}")
        print("Real-case accuracy claims: disabled")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "skill_dir",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to qimen-analysis-skill (defaults to the script parent)",
    )
    args = parser.parse_args()
    return Validator(args.skill_dir).run()


if __name__ == "__main__":
    raise SystemExit(main())
