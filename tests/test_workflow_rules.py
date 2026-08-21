import copy
import importlib.util
import hashlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(path: str) -> dict[str, str]:
    return {"path": path, "sha256": "a" * 64}


def evidence_manifest(
    role: str,
    result: str,
    change_id: str = "add-example-change",
    current_batch: int = 1,
    attempt: int = 1,
    contract_revision: int = 1,
    canonical_sha256: str = "b" * 64,
    agent_identity: str | None = None,
    agent_role: str | None = None,
) -> str:
    if agent_identity is None or agent_role is None:
        defaults = {
            "attempt-report": ("antigravity-cli", "executor"),
            "batch-review": ("grok-cli", "independent-reviewer"),
            "preflight-review": ("codex", "decision-owner"),
            "timeout-audit": ("codex", "decision-owner"),
            "final-verification": ("codex", "decision-owner"),
            "final-review": ("codex", "decision-owner"),
        }
        default_identity, default_role = defaults[role]
        agent_identity = agent_identity or default_identity
        agent_role = agent_role or default_role
    return (
        "<!-- COOP_EVIDENCE_MANIFEST_START -->\n"
        "```yaml\n"
        "evidence_schema_version: 1\n"
        f"evidence_role: {role}\n"
        f"evidence_result: {result}\n"
        f"change_id: {change_id}\n"
        f"current_batch: {current_batch}\n"
        f"attempt: {attempt}\n"
        f"contract_revision: {contract_revision}\n"
        f"canonical_sha256: {canonical_sha256}\n"
        f"agent_identity: {agent_identity}\n"
        f"agent_role: {agent_role}\n"
        "```\n"
        "<!-- COOP_EVIDENCE_MANIFEST_END -->\n"
    )


def schema5_evidence_manifest(
    role: str,
    result: str,
    change_id: str = "add-example-change",
    current_batch: int = 1,
    attempt: int = 1,
    contract_revision: int = 1,
    canonical_sha256: str = "b" * 64,
    high_review: bool = True,
) -> str:
    assignments = {
        "attempt-report": ("antigravity-cli", "antigravity-executor-01", "executor", "cohesive-medium"),
        "batch-review": ("grok-cli", "grok-reviewer-01", "independent-reviewer", "control-plane-high"),
        "preflight-review": ("codex", "codex-control-01", "control-plane", "control-plane-high"),
        "timeout-audit": ("codex", "codex-control-01", "control-plane", "control-plane-high"),
        "final-verification": ("codex", "codex-control-01", "control-plane", "control-plane-high"),
        "final-review": ("codex", "codex-control-01", "control-plane", "control-plane-high"),
    }
    product, instance, agent_role, profile = assignments[role]
    text = (
        "<!-- COOP_EVIDENCE_MANIFEST_START -->\n"
        "```yaml\n"
        "evidence_schema_version: 2\n"
        f"evidence_role: {role}\n"
        f"evidence_result: {result}\n"
        f"change_id: {change_id}\n"
        f"current_batch: {current_batch}\n"
        f"attempt: {attempt}\n"
        f"contract_revision: {contract_revision}\n"
        f"canonical_sha256: {canonical_sha256}\n"
        f"agent_product: {product}\n"
        f"agent_instance_id: {instance}\n"
        f"agent_role: {agent_role}\n"
        f"capability_profile: {profile}\n"
        "```\n"
        "<!-- COOP_EVIDENCE_MANIFEST_END -->\n"
    )
    if high_review and role in {"batch-review", "final-review"}:
        text += (
            "\nActual files and complete diff inspected\n"
            "Copy/transform/production wiring trace\n"
            "Critical reruns\n"
            "Claim-to-mechanism support\n"
            "Independent adversarial probe\n"
        )
    return text


def materialize_schema5_lease(data: dict, root: Path) -> None:
    text = (
        "<!-- COOP_CONFIRMATION_LEASE_START -->\n"
        "```yaml\n"
        "decision_id: decision-001\n"
        "artifact_revision: 2\n"
        f"artifact_sha256: {'a' * 64}\n"
        "approved_scope: approved source implementation\n"
        "approved_actions:\n"
        "  - run-safe-tests\n"
        "risk_profile: standard\n"
        "decision_source: ai-proposed/user-approved\n"
        "owner_instance_id: codex-control-01\n"
        "status: valid\n"
        "invalidation_conditions:\n"
        "  - scope-change\n"
        "```\n"
        "<!-- COOP_CONFIRMATION_LEASE_END -->\n"
    )
    target = root / data["confirmation_lease"]["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    data["confirmation_lease"]["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()


def schema4_contract(validator, handoff: str, **overrides) -> dict:
    data = validator.extract_handoff_contract(handoff, "handoff")
    for key in (
        "control_plane_owner", "executor_assignment",
        "independent_reviewer_assignment", "reviewer_assignment", "decision_source",
        "confirmation_lease", "confirmation_lease_status",
    ):
        data.pop(key, None)
    identity_fields = {
        "executor_agent": "antigravity-cli",
        "independent_reviewer_agent": "grok-cli",
        "decision_owner": "codex",
        "independent_review_not_applicable_reason": None,
    }
    data.update(schema_version=4, **identity_fields)
    data["readonly_fields"] = list(validator.LEGACY_IMMUTABLE_FIELDS)
    data.update(overrides)
    return data


def standard_reviewer_assignment(product="codex", instance="codex-reviewer-02"):
    return {
        "review_purpose": {
            "object": "current batch implementation, Report, contract, and evidence",
            "decision": "decide pass, fail, or blocked for this governed Review gate",
        },
        "agent_product": product,
        "agent_instance_id": instance,
        "agent_role": "independent-reviewer",
        "capability_profile": "control-plane-high",
        "independence_requirement": {
            "kind": "distinct-contract-instance",
            "distinct_from": ["control_plane_owner", "executor_assignment"],
        },
        "result_authority": "governed-review-evidence",
    }


def assert_schema6_fixture(data: dict, *, compact: bool = False) -> None:
    expected_assignment_fields = {
        "review_purpose", "agent_product", "agent_instance_id", "agent_role",
        "capability_profile", "independence_requirement", "result_authority",
    }
    if data.get("schema_version") != 6:
        raise AssertionError("schema-6 fixture has the wrong discriminator")
    if "independent_reviewer_assignment" in data:
        raise AssertionError("schema-5 reviewer field leaked into schema-6 fixture")
    if set(data.get("reviewer_assignment", {})) != expected_assignment_fields:
        raise AssertionError("schema-6 reviewer assignment shape is invalid")
    readonly = data.get("readonly_fields")
    if (
        not isinstance(readonly, list)
        or len(readonly) != len(set(readonly))
        or "reviewer_assignment" not in readonly
        or "independent_reviewer_assignment" in readonly
    ):
        raise AssertionError("schema-6 readonly replacement is invalid")
    if "independence_na_reason" in data:
        raise AssertionError("undefined compact reason field leaked into fixture")
    reason = data.get("independent_review_not_applicable_reason")
    if compact:
        if not isinstance(reason, str) or not reason.strip():
            raise AssertionError("compact fixture requires a nonblank NA reason")
    elif reason is not None:
        raise AssertionError("standard/strict fixture requires a null NA reason")


def schema6_contract(validator, handoff: str, **overrides) -> dict:
    data = validator.extract_handoff_contract(handoff, "handoff")
    if data.get("schema_version") == 5:
        old_assignment = data.pop("independent_reviewer_assignment")
        if set(old_assignment) != {
            "agent_product", "agent_instance_id", "agent_role", "capability_profile",
        }:
            raise AssertionError("unexpected frozen schema-5 reviewer shape")
        data["schema_version"] = 6
        data["reviewer_assignment"] = standard_reviewer_assignment(
            product=old_assignment["agent_product"],
            instance=old_assignment["agent_instance_id"],
        )
        data["readonly_fields"] = [
            "reviewer_assignment" if item == "independent_reviewer_assignment" else item
            for item in data["readonly_fields"]
        ]
    elif data.get("schema_version") != 6:
        raise AssertionError("schema6 test fixture requires schema 5 or schema 6")
    data.update(copy.deepcopy(overrides))
    assert_schema6_fixture(data)
    return data


def schema5_contract(validator, handoff: str, **overrides) -> dict:
    data = validator.extract_handoff_contract(handoff, "handoff")
    if data.get("schema_version") == 6:
        reviewer = data.pop("reviewer_assignment")
        data["schema_version"] = 5
        data["independent_reviewer_assignment"] = {
            key: reviewer[key]
            for key in (
                "agent_product", "agent_instance_id", "agent_role",
                "capability_profile",
            )
        }
        data["readonly_fields"] = [
            "independent_reviewer_assignment"
            if item == "reviewer_assignment" else item
            for item in data["readonly_fields"]
        ]
    elif data.get("schema_version") != 5:
        raise AssertionError("schema5 fixture requires schema 5 or schema 6")
    data.update(copy.deepcopy(overrides))
    return data


def render_handoff_contract(validator, data: dict) -> str:
    def scalar(value) -> str:
        if value is None:
            return "null"
        if value is True:
            return "true"
        if value is False:
            return "false"
        return str(value)

    def render(value, indent: int = 0) -> list[str]:
        prefix = " " * indent
        lines: list[str] = []
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}{key}:")
                    lines.extend(render(item, indent + 2))
                else:
                    lines.append(f"{prefix}{key}: {scalar(item)}")
            return lines
        if isinstance(value, list):
            for item in value:
                if isinstance(item, (dict, list)):
                    raise AssertionError("test YAML renderer accepts scalar lists only")
                lines.append(f"{prefix}- {scalar(item)}")
            return lines
        raise AssertionError("test YAML renderer requires a mapping or list")

    payload = "\n".join(render(data))
    parsed = validator.simple_yaml_load(payload)
    if parsed != data:
        raise AssertionError("test YAML renderer did not round-trip the fixture")
    return (
        "<!-- COOP_HANDOFF_CONTRACT_START -->\n"
        "```yaml\n"
        f"{payload}\n"
        "```\n"
        "<!-- COOP_HANDOFF_CONTRACT_END -->\n"
    )


def compact_schema6_contract(validator, handoff: str, **overrides) -> dict:
    data = schema6_contract(validator, handoff)
    owner = data["control_plane_owner"]
    data["risk_profile"] = "compact"
    data["reviewer_assignment"] = {
        "review_purpose": {
            "object": "current compact implementation, evidence, and contract",
            "decision": "decide pass, fail, or blocked for the compact Review gate",
        },
        "agent_product": owner["agent_product"],
        "agent_instance_id": owner["agent_instance_id"],
        "agent_role": owner["agent_role"],
        "capability_profile": owner["capability_profile"],
        "independence_requirement": {
            "kind": "distinct-contract-instance",
            "distinct_from": ["executor_assignment"],
        },
        "result_authority": "governed-review-evidence",
    }
    data["independent_review_not_applicable_reason"] = (
        "compact inline Review is owned by the bound control-plane instance"
    )
    data.update(copy.deepcopy(overrides))
    assert_schema6_fixture(data, compact=True)
    return data


def set_nested(mapping: dict, path: tuple[str, ...], value) -> None:
    target = mapping
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def schema2_assignment_evidence_manifest(
    role: str,
    result: str,
    assignment: dict,
    *,
    change_id: str = "add-example-change",
    current_batch: int = 1,
    attempt: int = 1,
    contract_revision: int = 2,
    canonical_sha256: str = "b" * 64,
) -> str:
    text = (
        "<!-- COOP_EVIDENCE_MANIFEST_START -->\n"
        "```yaml\n"
        "evidence_schema_version: 2\n"
        f"evidence_role: {role}\n"
        f"evidence_result: {result}\n"
        f"change_id: {change_id}\n"
        f"current_batch: {current_batch}\n"
        f"attempt: {attempt}\n"
        f"contract_revision: {contract_revision}\n"
        f"canonical_sha256: {canonical_sha256}\n"
        f"agent_product: {assignment['agent_product']}\n"
        f"agent_instance_id: {assignment['agent_instance_id']}\n"
        f"agent_role: {assignment['agent_role']}\n"
        f"capability_profile: {assignment['capability_profile']}\n"
        "```\n"
        "<!-- COOP_EVIDENCE_MANIFEST_END -->\n"
    )
    if role in {"batch-review", "final-review"}:
        text += (
            "\nActual files and complete diff inspected\n"
            "Copy/transform/production wiring trace\n"
            "Critical reruns\n"
            "Claim-to-mechanism support\n"
            "Independent adversarial probe\n"
        )
    return text


def load_validator():
    path = ROOT / "scripts" / "validate_templates.py"
    spec = importlib.util.spec_from_file_location("validate_templates", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class WorkflowRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()
        cls.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.readme_cn = (ROOT / "README_cn.md").read_text(encoding="utf-8")
        cls.handoff = (ROOT / "references" / "handoff-contract.md").read_text(encoding="utf-8")
        cls.governor = (
            ROOT / "references" / "handed-off-external-execution.md"
        ).read_text(encoding="utf-8")
        cls.review = (ROOT / "references" / "review-template.md").read_text(encoding="utf-8")

    def test_description_targets_prompt_and_evidence_review(self):
        description = " ".join(self.skill.split("---", 2)[1].split())
        self.assertIn("explicitly requested standalone", description)
        self.assertIn(
            "also use for dispatch/review/resume of an external-agent batch "
            "with an existing valid Handoff Contract",
            description,
        )
        for expected in (
            "non-state-changing", "read-only", "does not request fixes",
            "final completion", "valid Handoff Contract", "file edits",
            "workflow/template changes",
        ):
            self.assertIn(expected, description)
        self.assertNotIn("breaking down implementation/task/step/batch", description)

    def test_standalone_path_does_not_require_handoff(self):
        self.assertIn("Standalone Lightweight", self.skill)
        section = self.skill.split("## Standalone Lightweight", 1)[1].split("## ", 1)[0]
        self.assertIn("does not require", section)
        self.assertIn("Handoff Contract", section)

    def test_thin_entry_routes_handoff_detail_to_reference(self):
        self.assertIn("## Route Selection", self.skill)
        self.assertIn("## Standalone Lightweight", self.skill)
        self.assertIn("## Non-Negotiables", self.skill)
        self.assertIn(
            "Never run `git add`, `git commit`, `git reset`, or `git clean`",
            self.skill,
        )
        normalized = " ".join(self.skill.split())
        required_route_contract = (
            "When Handed-off External Execution is selected, read "
            "`references/handed-off-external-execution.md` completely before "
            "any batch action. Do not read it for Standalone Lightweight work."
        )
        checks = {
            "explicit route-scoped reference": (
                required_route_contract in normalized
            ),
            "Artifact Paths moved out of entry": (
                "### Artifact Paths" not in self.skill
            ),
            "State Machine moved out of entry": (
                "### State Machine" not in self.skill
            ),
            "Evidence Profiles moved out of entry": (
                "## Evidence Profiles" not in self.skill
            ),
        }
        for label, condition in checks.items():
            with self.subTest(label=label):
                self.assertTrue(condition, label)

    def test_handoff_governor_reference_preserves_complete_contract(self):
        path = ROOT / "references" / "handed-off-external-execution.md"
        self.assertTrue(path.is_file(), "Handoff governor reference missing")
        governor = path.read_text(encoding="utf-8")
        normalized_bytes = (governor.rstrip() + "\n").encode("utf-8")
        self.assertEqual(
            hashlib.sha256(normalized_bytes).hexdigest(),
            "0931999b997b93da601d443b5bdf7a3486f950ab47ef7d96c31c19a6911fc1fe",
        )
        for needle in (
            "schema-version-6", "schema-4/schema-5", "Artifact Paths", "State Machine",
            "Evidence Profiles", "agent_instance_id", "Preflight Review",
            "actual files and the complete diff", "claim-to-mechanism support",
            "independent adversarial", "awaiting-final-verification", "needs-fix",
            "same batch", "must be reviewed again", "without claiming task completion",
        ):
            self.assertIn(needle, governor)

    def test_standalone_review_is_request_scoped_and_not_auto_chained(self):
        section = " ".join(
            self.skill.split("## Standalone Lightweight", 1)[1]
            .split("## ", 1)[0]
            .split()
        )
        self.assertIn(
            "This route is request-scoped. Do not auto-chain it after producing "
            "an OpenSpec change or another artifact; use it only for the current "
            "explicit wording or read-only Review request.",
            section,
        )

    def test_standalone_openspec_review_is_brief_and_contract_complete(self):
        section = " ".join(
            self.skill.split("## Standalone Lightweight", 1)[1]
            .split("## ", 1)[0]
            .split()
        )
        self.assertIn(
            "For OpenSpec artifacts, inspect proposal scope, spec scenarios, "
            "design decisions and risks, task traceability, and cross-artifact "
            "consistency.",
            section,
        )
        self.assertIn(
            "Default to findings-first output: scope/evidence, actionable "
            "findings, verdict, and next action.",
            section,
        )
        self.assertIn(
            "Omit governance narration unless it changes the result or next action.",
            section,
        )

    def test_readmes_make_standalone_review_explicit_and_request_scoped(self):
        readme = " ".join(self.readme.split())
        readme_cn = " ".join(self.readme_cn.split())
        self.assertIn(
            "Standalone Review requires an explicit user request, is "
            "request-scoped and findings-first, and is never auto-chained after "
            "change generation.",
            readme,
        )
        self.assertIn(
            "An explicitly requested standalone OpenSpec Review remains concise "
            "and checks:",
            readme,
        )
        self.assertIn(
            "Handed-off execution loads its complete governor on demand from "
            "`references/handed-off-external-execution.md`; standalone work does "
            "not read that procedure.",
            readme,
        )
        self.assertIn(
            "Standalone Review 必须由用户明确请求、仅作用于当前请求、采用 "
            "findings-first 输出，且生成变更后绝不自动串联触发。",
            readme_cn,
        )
        self.assertIn(
            "明确请求的 standalone OpenSpec Review 保持简洁，并检查：",
            readme_cn,
        )
        self.assertIn(
            "Handed-off 路径按需完整读取 "
            "`references/handed-off-external-execution.md`；standalone 路径不读取该治理流程。",
            readme_cn,
        )

    def test_review_and_fix_returns_to_change_gate(self):
        self.assertIn("Review and fix", self.skill)
        self.assertIn("openspec-superpower-change", self.skill)

    def test_canonical_contract_lives_only_in_status(self):
        self.assertIn("canonical", self.handoff)
        self.assertIn("docs/agent-collab/<change-id>/status.md", self.handoff)
        self.assertIn("must not embed", self.handoff)

    def test_attempt_specific_artifacts_preserve_review_history(self):
        self.assertIn("attempt-<AA>", self.governor)
        self.assertIn("same batch", self.governor)
        self.assertIn("needs-fix", self.governor)

    def test_fail_and_blocked_must_reenter_review(self):
        self.assertIn("FAIL", self.review)
        self.assertIn("needs-fix", self.review)
        self.assertIn("resume_condition", self.review)
        self.assertIn("must be reviewed again", self.review)

    def test_preflight_uses_pass_or_blocked_without_batch_review_substitution(self):
        brief = (ROOT / "references" / "brief-template.md").read_text(encoding="utf-8")
        self.assertIn("结果：PASS / BLOCKED", brief)
        self.assertNotIn("结果：PASS / FAIL / BLOCKED", brief)
        self.assertIn("Preflight uses only `PASS`/`BLOCKED`", self.governor)
        self.assertIn("不能充当 `batch-review`", self.review)

    def test_complete_contract_requires_review_and_final_verification(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="complete",
            last_review_result="blocked",
            final_verification="pending",
            final_review_result="pending",
            next_owner="user",
        )
        with self.assertRaisesRegex(AssertionError, "complete"):
            self.validator.validate_handoff_contract(data, "invalid-complete")

    def test_handoff_schema_has_evidence_bound_v6_fields(self):
        for expected in (
            "schema_version: 6",
            "attempt_report_artifact:",
            "last_review_artifact:",
            "final_verification_artifact:",
            "final_review_artifact:",
        ):
            self.assertIn(expected, self.handoff)

    def test_schema4_requires_bound_agent_identities_and_codex_decision_owner(self):
        data = schema4_contract(self.validator, self.handoff)
        self.validator.validate_legacy_handoff_contract(data, "schema4-identities")
        self.assertEqual(self.validator.LEGACY_SCHEMA_VERSION, 4)
        for field in (
            "executor_agent", "independent_reviewer_agent", "decision_owner",
        ):
            self.assertIn(field, self.validator.LEGACY_IMMUTABLE_FIELDS)

        for field, value in (
            ("executor_agent", "agy"),
            ("independent_reviewer_agent", "grok"),
            ("decision_owner", "antigravity-cli"),
        ):
            invalid = dict(data)
            invalid[field] = value
            with self.subTest(field=field, value=value):
                with self.assertRaisesRegex(AssertionError, "agent|identity|decision_owner"):
                    self.validator.validate_legacy_handoff_contract(invalid, "invalid-identity")

    def test_standard_and_strict_require_a_distinct_reviewer(self):
        self.assertEqual(self.validator.LEGACY_SCHEMA_VERSION, 4)
        for profile in ("standard", "strict"):
            same_agent = schema4_contract(
                self.validator, self.handoff, risk_profile=profile,
                independent_reviewer_agent="antigravity-cli",
            )
            with self.subTest(profile=profile, case="self-review"):
                with self.assertRaisesRegex(AssertionError, "reviewer|distinct|self-review"):
                    self.validator.validate_legacy_handoff_contract(same_agent, "self-review")

            no_reviewer = schema4_contract(
                self.validator, self.handoff, risk_profile=profile,
                independent_reviewer_agent="not-applicable",
                independent_review_not_applicable_reason="reviewed inline",
            )
            with self.subTest(profile=profile, case="not-applicable"):
                with self.assertRaisesRegex(AssertionError, "reviewer|not-applicable|compact"):
                    self.validator.validate_legacy_handoff_contract(no_reviewer, "missing-reviewer")

    def test_compact_not_applicable_reviewer_requires_a_reason(self):
        valid = schema4_contract(
            self.validator, self.handoff, risk_profile="compact",
            independent_reviewer_agent="not-applicable",
            independent_review_not_applicable_reason="Codex performs the inline Review",
        )
        self.validator.validate_legacy_handoff_contract(valid, "compact-inline-review")

        for reason in (None, "", "   "):
            invalid = dict(valid)
            invalid["independent_review_not_applicable_reason"] = reason
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(AssertionError, "reason|non-blank"):
                    self.validator.validate_legacy_handoff_contract(invalid, "missing-na-reason")

        concrete = schema4_contract(
            self.validator, self.handoff, risk_profile="compact",
            independent_review_not_applicable_reason="must be null",
        )
        with self.assertRaisesRegex(AssertionError, "reason|not-applicable|null"):
            self.validator.validate_legacy_handoff_contract(concrete, "unexpected-na-reason")

    def test_role_first_standalone_review_wording_is_exact(self):
        example = (
            "Review purpose: inspect the current implementation plan and decide PASS or "
            "BLOCKED; reviewer product: codex; role: independent-reviewer; capability: "
            "control-plane-high; independence: a user-opened new-window instance distinct "
            "from the plan author and executor; authority: governed Review evidence only."
        )
        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn(example, self.skill)
        self.assertIn(example, metadata)
        normalized_skill = " ".join(self.skill.split())
        for product in ("codex", "pi", "antigravity-cli", "grok-cli"):
            self.assertIn(product, self.governor)
        for phrase in (
            "canonical assignment",
            "explicitly selected by the user",
            "one concrete eligible product",
            "another agent",
            "independent agent",
            "another model",
            "BLOCKED",
        ):
            self.assertIn(phrase, normalized_skill)

    def test_role_first_review_kind_matrix_is_explicit(self):
        normalized = " ".join(self.skill.split())
        for phrase in (
            "A Review that decides whether implementation, execution, runtime "
            "planning, promotion, archive, or completion may proceed is "
            "gate-bearing",
            "use role `independent-reviewer`, profile `control-plane-high`, "
            "distinct-instance independence, and authority "
            "`governed-review-evidence`",
            "A standalone Review that explicitly does not decide a gate is advisory",
            "preserve any eligible user-selected product, use role "
            "`advisory-reviewer`, profile `control-plane-high`, "
            "advisory-not-gate-bearing independence, and authority `advisory-input`",
            "`cohesive-medium` and `mechanical-low` are "
            "executor/evidence-collection profiles, not Review profiles",
            "For standalone prompt or recommendation wording, a request to open "
            "or name a new distinct reviewer instance remains actionable after "
            "all six assignment concepts are resolved",
            "do not infer unavailability merely because a concrete instance ID "
            "or open window is not yet supplied",
            "Return `BLOCKED` only when the request explicitly says no eligible "
            "distinct instance exists or insists on reusing an implementation instance",
            "return `BLOCKED` with `blocker_owner: user` and a non-blank resume condition",
        ):
            self.assertIn(phrase, normalized)

    def test_schema6_templates_display_complete_reviewer_assignment(self):
        templates = (
            "agy-dispatch-template.md",
            "brief-template.md",
            "report-template.md",
            "review-template.md",
            "timeout-audit-template.md",
        )
        required = (
            "schema 6",
            "Review purpose object",
            "Review purpose decision",
            "reviewer product",
            "reviewer instance",
            "reviewer role",
            "capability profile",
            "distinct_from",
            "result authority",
        )
        for filename in templates:
            text = (ROOT / "references" / filename).read_text(encoding="utf-8")
            normalized = " ".join(text.split())
            with self.subTest(template=filename):
                for field in required:
                    self.assertIn(field, normalized)

    def test_current_companion_surfaces_reject_legacy_current_wording(self):
        surfaces = (
            "SKILL.md",
            "agents/openai.yaml",
            "references/agy-dispatch-template.md",
            "references/brief-template.md",
            "references/report-template.md",
            "references/review-template.md",
            "references/timeout-audit-template.md",
        )
        forbidden = (
            "schema-version-5",
            "schema-5 Handoff",
            "Compact null reviewer",
            "只有 compact 可记录带非空理由的 null reviewer",
        )
        for relative in surfaces:
            text = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(surface=relative):
                for phrase in forbidden:
                    self.assertNotIn(phrase, text)

    def test_public_docs_bind_current_schema6_and_schema2_evidence(self):
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README_cn.md").read_text(encoding="utf-8")
        self.assertIn("Current governed status uses schema 6", english)
        self.assertIn("schema-2 evidence manifests", english)
        self.assertIn("Frozen schema-4/schema-5", english)
        self.assertNotIn("schema-1 role/result/change/batch/attempt/source", english)
        self.assertIn("当前受治理状态使用 schema 6", chinese)
        self.assertIn("schema-2 evidence manifest", chinese)
        self.assertIn("冻结的 schema-4/schema-5", chinese)
        self.assertNotIn("schema 1 role/result/change/batch/attempt/source", chinese)


    def test_schema6_current_contract_accepts_all_four_reviewer_products(self):
        products = (
            ("codex", "codex-reviewer-02"),
            ("pi", "pi-reviewer-02"),
            ("antigravity-cli", "antigravity-reviewer-02"),
            ("grok-cli", "grok-reviewer-02"),
        )
        for product, instance in products:
            data = schema6_contract(self.validator, self.handoff)
            data["reviewer_assignment"] = standard_reviewer_assignment(product, instance)
            assert_schema6_fixture(data)
            with self.subTest(product=product):
                self.validator.validate_handoff_contract(data, "schema6-valid")

    def test_schema6_reviewer_assignment_exact_shape_fails_closed(self):
        invalid_mutations = (
            ("missing-assignment", lambda d: d.pop("reviewer_assignment")),
            ("missing-purpose", lambda d: d["reviewer_assignment"].pop("review_purpose")),
            (
                "blank-purpose",
                lambda d: d["reviewer_assignment"]["review_purpose"].update(object=" "),
            ),
            (
                "extra-purpose",
                lambda d: d["reviewer_assignment"]["review_purpose"].update(extra="x"),
            ),
            (
                "bad-independence-kind",
                lambda d: d["reviewer_assignment"]["independence_requirement"].update(
                    kind="session-label"
                ),
            ),
            (
                "duplicate-independence-target",
                lambda d: d["reviewer_assignment"]["independence_requirement"].update(
                    distinct_from=["executor_assignment", "executor_assignment"]
                ),
            ),
            (
                "canonical-authority",
                lambda d: d["reviewer_assignment"].update(
                    result_authority="canonical-decision"
                ),
            ),
            (
                "unknown-product",
                lambda d: d["reviewer_assignment"].update(agent_product="unknown-agent"),
            ),
        )
        for label, mutate in invalid_mutations:
            data = schema6_contract(self.validator, self.handoff)
            assert_schema6_fixture(data)
            mutate(data)
            with self.subTest(case=label):
                with self.assertRaisesRegex(
                    AssertionError,
                    "reviewer_assignment|review_purpose|independence|result_authority|agent_product",
                ):
                    self.validator.validate_handoff_contract(data, label)

    def test_schema6_standard_strict_and_compact_profiles_are_exact(self):
        for profile in ("standard", "strict"):
            valid = schema6_contract(self.validator, self.handoff, risk_profile=profile)
            self.validator.validate_handoff_contract(valid, f"{profile}-valid")

            invalid_cases = []
            wrong_targets = copy.deepcopy(valid)
            wrong_targets["reviewer_assignment"]["independence_requirement"][
                "distinct_from"
            ] = ["executor_assignment"]
            invalid_cases.append(("independence", wrong_targets))

            same_instance = copy.deepcopy(valid)
            same_instance["reviewer_assignment"]["agent_instance_id"] = (
                same_instance["control_plane_owner"]["agent_instance_id"]
            )
            invalid_cases.append(("instance", same_instance))

            wrong_role = copy.deepcopy(valid)
            wrong_role["reviewer_assignment"]["agent_role"] = "control-plane"
            invalid_cases.append(("agent_role", wrong_role))

            wrong_profile = copy.deepcopy(valid)
            wrong_profile["reviewer_assignment"]["capability_profile"] = "cohesive-medium"
            invalid_cases.append(("capability_profile", wrong_profile))

            unexpected_reason = copy.deepcopy(valid)
            unexpected_reason["independent_review_not_applicable_reason"] = "not allowed"
            invalid_cases.append(("reason", unexpected_reason))

            for expected, invalid in invalid_cases:
                with self.subTest(profile=profile, invalid=expected):
                    with self.assertRaisesRegex(
                        AssertionError,
                        f"{expected}|reviewer_assignment|standard|strict",
                    ):
                        self.validator.validate_handoff_contract(invalid, "invalid-profile")

        compact = compact_schema6_contract(self.validator, self.handoff)
        self.validator.validate_handoff_contract(compact, "compact-valid")
        owner = compact["control_plane_owner"]
        reviewer = compact["reviewer_assignment"]
        self.assertEqual(
            {
                key: reviewer[key]
                for key in (
                    "agent_product", "agent_instance_id", "agent_role",
                    "capability_profile",
                )
            },
            owner,
        )

        compact_cases = []
        wrong_identity = copy.deepcopy(compact)
        wrong_identity["reviewer_assignment"]["agent_instance_id"] = "codex-reviewer-09"
        compact_cases.append(("control-plane|identity|instance", wrong_identity))
        wrong_targets = copy.deepcopy(compact)
        wrong_targets["reviewer_assignment"]["independence_requirement"][
            "distinct_from"
        ] = ["control_plane_owner", "executor_assignment"]
        compact_cases.append(("independence", wrong_targets))
        same_executor = copy.deepcopy(compact)
        same_executor["executor_assignment"]["agent_instance_id"] = owner["agent_instance_id"]
        compact_cases.append(("executor|instance|distinct", same_executor))
        blank_reason = copy.deepcopy(compact)
        blank_reason["independent_review_not_applicable_reason"] = " "
        compact_cases.append(("reason|non-blank", blank_reason))
        for expected, invalid in compact_cases:
            with self.subTest(compact_invalid=expected):
                with self.assertRaisesRegex(AssertionError, expected):
                    self.validator.validate_handoff_contract(invalid, "invalid-compact")

    def test_schema6_current_and_legacy_validation_are_isolated(self):
        current_cases = (
            ("schema4", schema4_contract(self.validator, self.handoff)),
            ("schema5", schema5_contract(self.validator, self.handoff)),
        )
        for label, data in current_cases:
            with self.subTest(current_rejects=label):
                with self.assertRaisesRegex(
                    AssertionError, "current.*6|schema_version.*6"
                ):
                    self.validator.validate_handoff_contract(data, label)

        missing = self.validator.extract_handoff_contract(self.handoff, "missing")
        missing.pop("schema_version")
        with self.assertRaisesRegex(AssertionError, "current.*6|schema_version.*6"):
            self.validator.validate_handoff_contract(missing, "missing-schema")

        mislabeled = schema5_contract(self.validator, self.handoff)
        mislabeled["schema_version"] = 6
        with self.assertRaisesRegex(
            AssertionError,
            "reviewer_assignment|missing contract fields|unexpected contract fields",
        ):
            self.validator.validate_handoff_contract(mislabeled, "mislabeled-schema5")

        self.assertTrue(
            hasattr(self.validator, "validate_legacy_handoff_contract"),
            "production legacy-only validator API is missing",
        )

    def test_schema6_legacy_inventory_is_read_only_and_non_authorizing(self):
        self.assertTrue(
            hasattr(self.validator, "inventory_legacy_handoffs"),
            "production legacy inventory API is missing",
        )
        inventory = getattr(self.validator, "inventory_legacy_handoffs")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            status = root / "status.md"
            status.write_text(
                render_handoff_contract(
                    self.validator, schema5_contract(self.validator, self.handoff)
                ),
                encoding="utf-8",
            )
            with mock.patch.object(
                self.validator,
                "validate_transition",
                side_effect=AssertionError("legacy inventory called current transition"),
            ), mock.patch.object(
                self.validator,
                "validate_evidence_artifacts",
                side_effect=AssertionError("legacy inventory called evidence authority"),
            ):
                records = inventory([root])
        self.assertEqual(len(records), 1)
        self.assertEqual(
            set(records[0]),
            {"path", "schema_version", "lifecycle_state", "sha256", "drain_status"},
        )
        self.assertEqual(records[0]["schema_version"], 5)
        self.assertEqual(records[0]["lifecycle_state"], "ready-for-brief")

    def test_schema6_pi_is_current_only_and_cannot_backfill_legacy(self):
        self.assertTrue(
            hasattr(self.validator, "validate_legacy_handoff_contract"),
            "production legacy-only validator API is missing",
        )
        validate_legacy = getattr(self.validator, "validate_legacy_handoff_contract")

        schema4 = schema4_contract(
            self.validator, self.handoff, independent_reviewer_agent="pi"
        )
        with self.assertRaisesRegex(AssertionError, "reviewer|product|identity|agent"):
            validate_legacy(schema4, "schema4-pi")

        schema5 = schema5_contract(self.validator, self.handoff)
        schema5["independent_reviewer_assignment"]["agent_product"] = "pi"
        with self.assertRaisesRegex(AssertionError, "agent_product|product"):
            validate_legacy(schema5, "schema5-pi")

        schema6 = schema6_contract(self.validator, self.handoff)
        schema6["reviewer_assignment"] = standard_reviewer_assignment(
            "pi", "pi-reviewer-02"
        )
        self.validator.validate_handoff_contract(schema6, "schema6-pi")

    def test_schema6_reviewer_assignment_is_fully_readonly(self):
        readonly_mutations = (
            (("review_purpose", "object"), "changed review object"),
            (("review_purpose", "decision"), "changed review decision"),
            (("agent_product",), "pi"),
            (("agent_instance_id",), "changed-reviewer-09"),
            (("agent_role",), "control-plane"),
            (("capability_profile",), "cohesive-medium"),
            (
                ("independence_requirement", "distinct_from"),
                ["executor_assignment"],
            ),
            (("result_authority",), "canonical-control-plane-decision"),
        )
        for changed_path, changed_value in readonly_mutations:
            before = schema6_contract(self.validator, self.handoff)
            after = copy.deepcopy(before)
            after["contract_revision"] += 1
            after["lifecycle_state"] = "ready-for-execution"
            after["next_owner"] = "external-agent"
            set_nested(after["reviewer_assignment"], changed_path, changed_value)
            with self.subTest(changed_path=changed_path):
                with self.assertRaisesRegex(
                    AssertionError, "readonly|reviewer_assignment"
                ):
                    self.validator.validate_transition(
                        before, after, "assignment-mutation"
                    )

    def test_schema6_pi_review_evidence_matches_assignment_without_promotion(self):
        data = schema6_contract(self.validator, self.handoff)
        data["reviewer_assignment"] = standard_reviewer_assignment(
            "pi", "pi-reviewer-02"
        )
        data.update(
            lifecycle_state="ready-for-brief",
            current_batch=2,
            contract_revision=4,
            last_review_result="pass",
            attempt_report_artifact=artifact("report.md"),
            last_review_artifact=artifact("review.md"),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialize_schema5_lease(data, root)
            report = root / "report.md"
            report.write_text(
                schema2_assignment_evidence_manifest(
                    "attempt-report",
                    "pass",
                    data["executor_assignment"],
                    contract_revision=1,
                ),
                encoding="utf-8",
            )
            data["attempt_report_artifact"]["sha256"] = hashlib.sha256(
                report.read_bytes()
            ).hexdigest()
            review = root / "review.md"
            review.write_text(
                schema2_assignment_evidence_manifest(
                    "batch-review", "pass", data["reviewer_assignment"]
                ),
                encoding="utf-8",
            )
            data["last_review_artifact"]["sha256"] = hashlib.sha256(
                review.read_bytes()
            ).hexdigest()
            self.validator.validate_handoff_contract(data, "schema6-pi-evidence")
            canonical_before = copy.deepcopy(data)
            self.validator.validate_evidence_artifacts(
                data, root, "schema6-pi-evidence"
            )
            self.assertEqual(data, canonical_before)

            review.write_text(
                schema2_assignment_evidence_manifest(
                    "batch-review",
                    "pass",
                    standard_reviewer_assignment("codex", "pi-reviewer-02"),
                ),
                encoding="utf-8",
            )
            data["last_review_artifact"]["sha256"] = hashlib.sha256(
                review.read_bytes()
            ).hexdigest()
            with self.assertRaisesRegex(
                AssertionError, "identity|role|profile|assignment"
            ):
                self.validator.validate_evidence_artifacts(
                    data, root, "schema6-pi-impersonation"
                )


    def test_schema4_agent_identity_fields_are_immutable(self):
        before = schema4_contract(self.validator, self.handoff)
        after = dict(before)
        after.update(
            lifecycle_state="ready-for-execution",
            contract_revision=before["contract_revision"] + 1,
            next_owner="external-agent", executor_agent="grok-cli",
            independent_reviewer_agent="codex",
        )
        with self.assertRaisesRegex(
            AssertionError,
            "readonly field changed: (executor_agent|independent_reviewer_agent)",
        ):
            self.validator._validate_legacy_transition(before, after, "identity-change")

    def test_attempt_report_manifest_binds_executor_identity_and_role(self):
        data = schema4_contract(
            self.validator, self.handoff, lifecycle_state="ready-for-review",
            contract_revision=2, next_owner="codex-brief-antigravity-review",
            attempt_report_artifact=artifact("report.md"),
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            report = root / "report.md"
            report.write_text(evidence_manifest("attempt-report", "pass"), encoding="utf-8")
            data["attempt_report_artifact"] = {
                "path": "report.md", "sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
            }
            self.validator.validate_legacy_handoff_contract(data, "executor-evidence")
            self.validator._validate_legacy_evidence_artifacts(data, root, "executor-evidence")

            report.write_text(evidence_manifest(
                "attempt-report", "pass", agent_identity="grok-cli", agent_role="independent-reviewer",
            ), encoding="utf-8")
            data["attempt_report_artifact"]["sha256"] = hashlib.sha256(report.read_bytes()).hexdigest()
            with self.assertRaisesRegex(AssertionError, "identity|role|executor|impersonation"):
                self.validator._validate_legacy_evidence_artifacts(data, root, "executor-impersonation")

    def test_batch_review_rejects_executor_self_review_and_impersonation(self):
        data = schema4_contract(
            self.validator, self.handoff, lifecycle_state="awaiting-final-verification",
            current_batch=2, contract_revision=3, last_review_result="pass",
            next_owner="openspec-superpower-change",
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            report = root / "report.md"
            review = root / "review.md"
            report.write_text(evidence_manifest(
                "attempt-report", "pass", current_batch=2, contract_revision=1,
            ), encoding="utf-8")
            review.write_text(evidence_manifest(
                "batch-review", "pass", current_batch=2, contract_revision=2,
                agent_identity="antigravity-cli", agent_role="independent-reviewer",
            ), encoding="utf-8")
            data["attempt_report_artifact"] = {
                "path": "report.md", "sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
            }
            data["last_review_artifact"] = {
                "path": "review.md", "sha256": hashlib.sha256(review.read_bytes()).hexdigest(),
            }
            self.validator.validate_legacy_handoff_contract(data, "review-impersonation")
            with self.assertRaisesRegex(AssertionError, "identity|reviewer|self-review|impersonation"):
                self.validator._validate_legacy_evidence_artifacts(data, root, "review-impersonation")

    def test_timeout_audit_binds_codex_decision_owner_for_shared_artifact(self):
        data = schema4_contract(
            self.validator, self.handoff, lifecycle_state="blocked", contract_revision=2,
            last_review_result="blocked", blocked_reason="executor timeout",
            blocker_owner="external-agent", resume_condition="redispatch",
            next_owner="codex-brief-antigravity-review",
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            timeout = root / "timeout.md"
            timeout.write_text(evidence_manifest("timeout-audit", "blocked"), encoding="utf-8")
            ref = {"path": "timeout.md", "sha256": hashlib.sha256(timeout.read_bytes()).hexdigest()}
            data["attempt_report_artifact"] = ref
            data["last_review_artifact"] = ref
            self.validator.validate_legacy_handoff_contract(data, "timeout-identity")
            self.validator._validate_legacy_evidence_artifacts(data, root, "timeout-identity")

    def test_fallback_scalar_parser_handles_yaml_booleans_and_null(self):
        self.assertIs(self.validator.parse_scalar("true"), True)
        self.assertIs(self.validator.parse_scalar("false"), False)
        self.assertIsNone(self.validator.parse_scalar("null"))

    def test_fail_transition_requires_new_attempt_on_same_batch(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="ready-for-review",
            last_review_result="not-run",
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
        )
        after = dict(before)
        after.update(
            lifecycle_state="needs-fix",
            last_review_result="fail",
            last_review_artifact=artifact("docs/review/fail.md"),
            attempt=before["attempt"],
            contract_revision=before["contract_revision"] + 1,
            next_owner="codex-brief-antigravity-review",
        )
        with self.assertRaisesRegex(AssertionError, "attempt"):
            self.validator.validate_transition(before, after, "invalid-fail")

    def test_final_batch_pass_hands_back_to_router(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="ready-for-review",
            current_batch=before["planned_batches"],
            last_review_result="not-run",
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
        )
        after = dict(before)
        after.update(
            lifecycle_state="awaiting-final-verification",
            last_review_result="pass",
            last_review_artifact=artifact("docs/review/batch.md"),
            contract_revision=before["contract_revision"] + 1,
            next_owner="openspec-superpower-change",
        )
        self.validator.validate_transition(before, after, "final-pass")

    def test_execution_contract_rejects_unapproved_proposal_mode(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            mode="openspec-proposal",
            approval_status="proposed",
            executor="codex",
            governor="openspec-superpower-change",
        )
        with self.assertRaisesRegex(AssertionError, "execution contract"):
            self.validator.validate_handoff_contract(data, "proposal")

    def test_regular_transition_cannot_change_batch_attempt_or_owner(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        after = dict(before)
        after.update(
            lifecycle_state="ready-for-execution",
            current_batch=before["current_batch"] + 1,
            attempt=99,
            next_owner="user",
            contract_revision=before["contract_revision"] + 1,
        )
        with self.assertRaisesRegex(AssertionError, "same batch and attempt|next_owner"):
            self.validator.validate_transition(before, after, "illegal-jump")

    def test_blocked_contract_requires_blocked_review_result(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="blocked",
            last_review_result="pass",
            blocked_reason="dependency unavailable",
            blocker_owner="dependency",
            resume_condition="dependency restored",
            next_owner="user",
        )
        with self.assertRaisesRegex(AssertionError, "blocked|tuple"):
            self.validator.validate_handoff_contract(data, "blocked-pass")

    def test_compact_contract_still_requires_typed_evidence_fields(self):
        data = compact_schema6_contract(self.validator, self.handoff)
        data.update(
            step_critical="pytest",
            final_critical="pytest",
            stop_conditions="none",
            verification_strategy="run tests",
        )
        with self.assertRaisesRegex(AssertionError, "list|mapping"):
            self.validator.validate_handoff_contract(data, "untyped-compact")

    def test_complete_state_is_terminal(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="complete",
            current_batch=before["planned_batches"],
            last_review_result="pass",
            final_review_result="pass",
            final_verification="pass",
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
            last_review_artifact=artifact("docs/review/batch.md"),
            final_verification_artifact=artifact("docs/agent-collab/change/final-verification.md"),
            final_review_artifact=artifact("docs/review/final.md"),
            next_owner="user",
        )
        after = dict(before)
        after.update(attempt=2, contract_revision=before["contract_revision"] + 1)
        with self.assertRaisesRegex(AssertionError, "terminal"):
            self.validator.validate_transition(before, after, "mutate-complete")

    def test_change_id_must_be_path_safe_slug(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data["change_id"] = "../escape"
        with self.assertRaisesRegex(AssertionError, "change_id"):
            self.validator.validate_handoff_contract(data, "unsafe-change-id")

    def test_brief_uses_execution_revision_and_review_uses_current_revision(self):
        brief = (ROOT / "references" / "brief-template.md").read_text(encoding="utf-8")
        self.assertIn("ready-for-execution", brief)
        self.assertIn("Execution revision", self.review)
        self.assertIn("Review revision", self.review)

    def test_final_gate_failure_can_return_to_fix_with_new_attempt(self):
        before = self._awaiting_contract("pass")
        after = dict(before)
        after.update(
            lifecycle_state="needs-fix",
            attempt=before["attempt"] + 1,
            contract_revision=before["contract_revision"] + 1,
            final_review_result="fail",
            final_review_artifact=artifact("docs/review/final-fail.md"),
            next_owner="openspec-superpower-change",
        )
        self.validator.validate_transition(before, after, "final-gate-fix")

    def test_all_external_profiles_require_nonblank_critical_commands(self):
        data = compact_schema6_contract(self.validator, self.handoff)
        data.update(step_critical=[], final_critical=[])
        with self.assertRaisesRegex(AssertionError, "step_critical|final_critical"):
            self.validator.validate_handoff_contract(data, "empty-critical")

        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(step_critical=["   "], final_critical=["\t"])
        with self.assertRaisesRegex(AssertionError, "non-blank"):
            self.validator.validate_handoff_contract(data, "blank-critical")

    def test_blank_stop_and_blocker_values_are_rejected(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data["stop_conditions"] = [" "]
        with self.assertRaisesRegex(AssertionError, "stop_conditions"):
            self.validator.validate_handoff_contract(data, "blank-stop")

        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="blocked",
            last_review_result="blocked",
            last_review_artifact=artifact("docs/review/blocked.md"),
            attempt_report_artifact=artifact("docs/agent-collab/change/report-abort.md"),
            blocked_reason=" ",
            blocker_owner="dependency",
            resume_condition="\t",
            next_owner="user",
        )
        with self.assertRaisesRegex(AssertionError, "blocked_reason|resume_condition"):
            self.validator.validate_handoff_contract(data, "blank-blocker")

    def test_boolean_is_not_a_positive_integer(self):
        for key in ("current_batch", "planned_batches", "attempt", "contract_revision"):
            data = self.validator.extract_handoff_contract(self.handoff, "handoff")
            data[key] = True
            with self.subTest(key=key):
                with self.assertRaisesRegex(AssertionError, "positive integer"):
                    self.validator.validate_handoff_contract(data, f"bool-{key}")

    def test_readonly_fields_must_match_exactly_without_duplicates(self):
        base = self.validator.extract_handoff_contract(self.handoff, "handoff")
        for readonly in (
            list(base["readonly_fields"]) + ["attempt"],
            list(base["readonly_fields"]) + [base["readonly_fields"][0]],
            list(base["readonly_fields"])[1:],
        ):
            data = dict(base)
            data["readonly_fields"] = readonly
            with self.subTest(readonly=readonly):
                with self.assertRaisesRegex(AssertionError, "readonly_fields"):
                    self.validator.validate_handoff_contract(data, "readonly-mismatch")

    def test_result_and_artifact_fields_are_strictly_paired(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data["last_review_artifact"] = artifact("docs/review/unexpected.md")
        with self.assertRaisesRegex(AssertionError, "last_review_artifact"):
            self.validator.validate_handoff_contract(data, "unexpected-review-artifact")

        data = self._awaiting_contract("pass")
        data["final_verification_artifact"] = None
        with self.assertRaisesRegex(AssertionError, "final_verification_artifact"):
            self.validator.validate_handoff_contract(data, "missing-final-evidence")

    def test_artifact_reference_must_be_safe_relative_path_and_sha256(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="ready-for-brief",
            current_batch=2,
            contract_revision=4,
            last_review_result="pass",
            last_review_artifact={"path": "../escape", "sha256": "x"},
        )
        with self.assertRaisesRegex(AssertionError, "artifact|sha256|relative"):
            self.validator.validate_handoff_contract(data, "unsafe-artifact")

    def test_runtime_artifact_validation_checks_file_size_and_hash(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="ready-for-brief",
            current_batch=2,
            contract_revision=4,
            last_review_result="pass",
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
            last_review_artifact=artifact("docs/review/batch.md"),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialize_schema5_lease(data if "data" in locals() else current, root)
            report = root / "docs" / "agent-collab" / "change" / "report.md"
            report.parent.mkdir(parents=True)
            report.write_text(
                schema5_evidence_manifest(
                    "attempt-report", "pass", contract_revision=1
                ),
                encoding="utf-8",
            )
            data["attempt_report_artifact"]["sha256"] = hashlib.sha256(
                report.read_bytes()
            ).hexdigest()
            review = root / "docs" / "review" / "batch.md"
            review.parent.mkdir(parents=True)
            review.write_text(
                schema5_evidence_manifest(
                    "batch-review", "pass", contract_revision=2
                ),
                encoding="utf-8",
            )
            data["last_review_artifact"]["sha256"] = hashlib.sha256(review.read_bytes()).hexdigest()
            self.validator.validate_evidence_artifacts(data, root, "runtime")
            data["last_review_artifact"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(AssertionError, "sha256"):
                self.validator.validate_evidence_artifacts(data, root, "runtime")

    def _awaiting_contract(self, verification: str = "pending") -> dict:
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="awaiting-final-verification",
            current_batch=data["planned_batches"],
            last_review_result="pass",
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
            last_review_artifact=artifact("docs/review/batch.md"),
            final_verification=verification,
            final_verification_artifact=(
                artifact("docs/agent-collab/change/final-verification.md")
                if verification != "pending" else None
            ),
            final_review_result="pending",
            final_review_artifact=None,
            next_owner="openspec-superpower-change",
        )
        return data

    def test_final_verification_pass_can_be_persisted_before_final_review(self):
        before = self._awaiting_contract()
        after = self._awaiting_contract("pass")
        after["contract_revision"] = before["contract_revision"] + 1
        self.validator.validate_transition(before, after, "persist-final-verification")

    def test_complete_requires_persisted_verification_and_all_artifacts(self):
        before = self._awaiting_contract()
        after = self._awaiting_contract("pass")
        after.update(
            lifecycle_state="complete",
            final_review_result="pass",
            final_review_artifact=artifact("docs/review/final.md"),
            next_owner="user",
            contract_revision=before["contract_revision"] + 1,
        )
        with self.assertRaisesRegex(AssertionError, "persisted final verification"):
            self.validator.validate_transition(before, after, "atomic-complete")

        before = self._awaiting_contract("pass")
        after = dict(before)
        after.update(
            lifecycle_state="complete",
            final_review_result="pass",
            final_review_artifact=artifact("docs/review/final.md"),
            next_owner="user",
            contract_revision=before["contract_revision"] + 1,
        )
        self.validator.validate_transition(before, after, "evidenced-complete")

    def test_batch_blocked_cannot_resume_directly_to_review(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="blocked",
            last_review_result="blocked",
            attempt_report_artifact=artifact("docs/agent-collab/change/abort.md"),
            last_review_artifact=artifact("docs/review/blocked.md"),
            blocked_reason="dependency unavailable",
            blocker_owner="dependency",
            resume_condition="dependency restored",
            next_owner="user",
        )
        after = dict(before)
        after.update(
            lifecycle_state="ready-for-review",
            last_review_result="not-run",
            last_review_artifact=None,
            blocked_reason=None,
            blocker_owner="none",
            resume_condition=None,
            next_owner="codex-brief-antigravity-review",
            attempt=before["attempt"] + 1,
            contract_revision=before["contract_revision"] + 1,
        )
        with self.assertRaisesRegex(AssertionError, "invalid lifecycle transition"):
            self.validator.validate_transition(before, after, "skip-report")

    def test_needs_fix_accepts_batch_and_each_final_failure_stage(self):
        batch = self.validator.extract_handoff_contract(self.handoff, "handoff")
        batch.update(
            lifecycle_state="needs-fix",
            last_review_result="fail",
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
            last_review_artifact=artifact("docs/review/batch-fail.md"),
        )
        self.validator.validate_handoff_contract(batch, "batch-fail")

        verification = self._awaiting_contract()
        verification.update(
            lifecycle_state="needs-fix",
            final_verification="fail",
            final_verification_artifact=artifact("docs/agent-collab/change/final-verification-fail.md"),
        )
        self.validator.validate_handoff_contract(verification, "verification-fail")

        review = self._awaiting_contract("pass")
        review.update(
            lifecycle_state="needs-fix",
            final_review_result="fail",
            final_review_artifact=artifact("docs/review/final-fail.md"),
        )
        self.validator.validate_handoff_contract(review, "final-review-fail")

    def test_blocked_accepts_batch_and_each_final_block_stage(self):
        common = {
            "lifecycle_state": "blocked",
            "blocked_reason": "dependency unavailable",
            "blocker_owner": "dependency",
            "resume_condition": "dependency restored",
            "next_owner": "user",
        }
        batch = self.validator.extract_handoff_contract(self.handoff, "handoff")
        batch.update(
            **common,
            last_review_result="blocked",
            attempt_report_artifact=artifact("docs/agent-collab/change/abort.md"),
            last_review_artifact=artifact("docs/review/batch-blocked.md"),
        )
        self.validator.validate_handoff_contract(batch, "batch-blocked")

        verification = self._awaiting_contract()
        verification.update(
            **common,
            final_verification="blocked",
            final_verification_artifact=artifact("docs/agent-collab/change/final-verification-blocked.md"),
        )
        self.validator.validate_handoff_contract(verification, "verification-blocked")

        review = self._awaiting_contract("pass")
        review.update(
            **common,
            final_review_result="blocked",
            final_review_artifact=artifact("docs/review/final-blocked.md"),
        )
        self.validator.validate_handoff_contract(review, "final-review-blocked")

    def test_preflight_blocked_does_not_require_an_attempt_report(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="blocked",
            last_review_result="blocked",
            last_review_artifact=artifact("docs/review/preflight-blocked.md"),
            blocked_reason="brief has an unauthorized git step",
            blocker_owner="codex-brief-antigravity-review",
            resume_condition="brief revised and preflight rerun",
            next_owner="codex-brief-antigravity-review",
        )
        self.assertIsNone(data["attempt_report_artifact"])
        self.validator.validate_handoff_contract(data, "preflight-blocked")

    def test_final_review_blocked_resume_preserves_verification_evidence(self):
        before = self._awaiting_contract("pass")
        before.update(
            lifecycle_state="blocked",
            final_review_result="blocked",
            final_review_artifact=artifact("docs/review/final-blocked.md"),
            blocked_reason="reviewer unavailable",
            blocker_owner="dependency",
            resume_condition="reviewer available",
            next_owner="user",
        )
        after = dict(before)
        after.update(
            lifecycle_state="awaiting-final-verification",
            final_review_result="pending",
            final_review_artifact=None,
            blocked_reason=None,
            blocker_owner="none",
            resume_condition=None,
            next_owner="openspec-superpower-change",
            contract_revision=before["contract_revision"] + 1,
        )
        self.validator.validate_transition(before, after, "resume-final-review")

        replaced = dict(after)
        replaced["attempt_report_artifact"] = artifact("docs/agent-collab/change/replacement-report.md")
        replaced["last_review_artifact"] = artifact("docs/review/replacement-batch.md")
        with self.assertRaisesRegex(AssertionError, "cannot rewrite"):
            self.validator.validate_transition(before, replaced, "resume-final-review-rewrite")

    def test_runtime_artifact_validation_rejects_missing_empty_and_symlink_escape(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="ready-for-brief",
            current_batch=2,
            contract_revision=4,
            last_review_result="pass",
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
            last_review_artifact=artifact("docs/review/batch.md"),
        )
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "root"
            root.mkdir()
            materialize_schema5_lease(data, root)
            with self.assertRaisesRegex(AssertionError, "exist and be non-empty"):
                self.validator.validate_evidence_artifacts(data, root, "missing")

            report = root / "docs" / "agent-collab" / "change" / "report.md"
            review = root / "docs" / "review" / "batch.md"
            report.parent.mkdir(parents=True)
            review.parent.mkdir(parents=True)
            report.write_text(schema5_evidence_manifest("attempt-report", "pass"), encoding="utf-8")
            review.write_text("", encoding="utf-8")
            data["attempt_report_artifact"]["sha256"] = hashlib.sha256(report.read_bytes()).hexdigest()
            with self.assertRaisesRegex(AssertionError, "exist and be non-empty"):
                self.validator.validate_evidence_artifacts(data, root, "empty")

            outside = base / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            review.unlink()
            review.symlink_to(outside)
            data["last_review_artifact"]["sha256"] = hashlib.sha256(outside.read_bytes()).hexdigest()
            with self.assertRaisesRegex(AssertionError, "outside artifact root"):
                self.validator.validate_evidence_artifacts(data, root, "symlink")

    def test_nonfinal_batch_promotion_requires_review_pass_and_keeps_decision_evidence(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="ready-for-review",
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
            next_owner="codex-brief-antigravity-review",
        )
        after = dict(before)
        after.update(
            lifecycle_state="ready-for-brief",
            current_batch=before["current_batch"] + 1,
            attempt=1,
            contract_revision=before["contract_revision"] + 1,
            attempt_report_artifact=None,
            last_review_result="not-run",
            last_review_artifact=None,
            next_owner="codex-brief-antigravity-review",
        )
        with self.assertRaisesRegex(AssertionError, "Review PASS|review evidence"):
            self.validator.validate_transition(before, after, "promote-without-review")

    def test_batch_decision_cannot_replace_the_report_that_was_reviewed(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="ready-for-review",
            current_batch=before["planned_batches"],
            attempt_report_artifact=artifact("docs/agent-collab/change/original-report.md"),
            next_owner="codex-brief-antigravity-review",
        )
        after = dict(before)
        after.update(
            lifecycle_state="awaiting-final-verification",
            contract_revision=before["contract_revision"] + 1,
            attempt_report_artifact=artifact("docs/agent-collab/change/replacement-report.md"),
            last_review_result="pass",
            last_review_artifact=artifact("docs/review/batch-pass.md"),
            next_owner="openspec-superpower-change",
        )
        with self.assertRaisesRegex(AssertionError, "attempt_report_artifact|reviewed Report"):
            self.validator.validate_transition(before, after, "replace-reviewed-report")

    def test_final_review_cannot_start_in_the_revision_that_first_persists_verification_pass(self):
        before = self._awaiting_contract()
        after = dict(before)
        after.update(
            lifecycle_state="blocked",
            contract_revision=before["contract_revision"] + 1,
            final_verification="pass",
            final_verification_artifact=artifact("docs/agent-collab/change/final-verification.md"),
            final_review_result="blocked",
            final_review_artifact=artifact("docs/review/final-review-blocked.md"),
            blocked_reason="reviewer unavailable",
            blocker_owner="dependency",
            resume_condition="reviewer available",
            next_owner="user",
        )
        with self.assertRaisesRegex(AssertionError, "persisted final verification|final Review"):
            self.validator.validate_transition(before, after, "atomic-final-verification-and-review")

    def test_blocked_self_transition_cannot_change_gate_tuple_or_evidence(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="blocked",
            current_batch=before["planned_batches"],
            attempt_report_artifact=artifact("docs/agent-collab/change/report-abort.md"),
            last_review_result="blocked",
            last_review_artifact=artifact("docs/review/batch-blocked.md"),
            blocked_reason="batch dependency unavailable",
            blocker_owner="dependency",
            resume_condition="batch dependency restored",
            next_owner="user",
        )
        after = dict(before)
        after.update(
            contract_revision=before["contract_revision"] + 1,
            last_review_result="pass",
            last_review_artifact=artifact("docs/review/fabricated-batch-pass.md"),
            final_verification="pass",
            final_verification_artifact=artifact("docs/agent-collab/change/fabricated-final-verification.md"),
            final_review_result="blocked",
            final_review_artifact=artifact("docs/review/final-review-blocked.md"),
            blocked_reason="final reviewer unavailable",
            resume_condition="final reviewer available",
        )
        with self.assertRaisesRegex(AssertionError, "blocked self-transition|result tuple|evidence"):
            self.validator.validate_transition(before, after, "rewrite-blocked-stage")

    def test_runtime_complete_snapshot_rejects_reused_artifact_with_mismatched_role_and_result(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "evidence.md"
            evidence.write_text(
                "# Review Result: FAIL\nNo verification commands were run.\n",
                encoding="utf-8",
            )
            shared_ref = {
                "path": "evidence.md",
                "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
            }
            data.update(
                lifecycle_state="complete",
                current_batch=data["planned_batches"],
                attempt_report_artifact=dict(shared_ref),
                last_review_result="pass",
                last_review_artifact=dict(shared_ref),
                final_verification="pass",
                final_verification_artifact=dict(shared_ref),
                final_review_result="pass",
                final_review_artifact=dict(shared_ref),
                next_owner="user",
            )
            with self.assertRaisesRegex(AssertionError, "artifact|evidence|result|role|distinct"):
                self.validator.validate_handoff_contract(data, "mixed-complete")
                self.validator.validate_evidence_artifacts(data, root, "mixed-complete")

    def test_runtime_evidence_manifest_binds_artifact_role_and_result(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="complete",
            current_batch=data["planned_batches"],
            contract_revision=5,
            last_review_result="pass",
            final_verification="pass",
            final_review_result="pass",
            next_owner="user",
        )
        specs = {
            "attempt_report_artifact": ("attempt-report.md", "attempt-report", "pass", 1),
            "last_review_artifact": ("batch-review.md", "batch-review", "pass", 2),
            "final_verification_artifact": ("final-verification.md", "final-verification", "pass", 3),
            "final_review_artifact": ("final-review.md", "final-review", "fail", 4),
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialize_schema5_lease(data if "data" in locals() else current, root)
            for key, (path, role, result, revision) in specs.items():
                target = root / path
                target.write_text(
                    schema5_evidence_manifest(role, result, current_batch=2, contract_revision=revision),
                    encoding="utf-8",
                )
                data[key] = {"path": path, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
            self.validator.validate_handoff_contract(data, "distinct-complete")
            with self.assertRaisesRegex(AssertionError, "evidence result"):
                self.validator.validate_evidence_artifacts(data, root, "distinct-complete")

    def test_timeout_audit_can_bind_report_and_review_without_other_role_reuse(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialize_schema5_lease(data if "data" in locals() else current, root)
            timeout = root / "timeout-audit.md"
            timeout.write_text(schema5_evidence_manifest("timeout-audit", "blocked"), encoding="utf-8")
            ref = {"path": timeout.name, "sha256": hashlib.sha256(timeout.read_bytes()).hexdigest()}
            data.update(
                lifecycle_state="blocked",
                contract_revision=2,
                attempt_report_artifact=dict(ref),
                last_review_result="blocked",
                last_review_artifact=dict(ref),
                blocked_reason="external agent timed out",
                blocker_owner="external-agent",
                resume_condition="timeout audit resolved",
                next_owner="codex-brief-antigravity-review",
            )
            self.validator.validate_handoff_contract(data, "timeout")
            self.validator.validate_evidence_artifacts(data, root, "timeout")

        conflicting = dict(data)
        conflicting["last_review_artifact"] = dict(data["last_review_artifact"])
        conflicting["last_review_artifact"]["sha256"] = "c" * 64
        with self.assertRaisesRegex(AssertionError, "distinct by role"):
            self.validator.validate_handoff_contract(conflicting, "timeout-conflict")

    def test_complete_rejects_preflight_review_as_batch_review_evidence(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="complete",
            current_batch=data["planned_batches"],
            contract_revision=5,
            last_review_result="pass",
            final_verification="pass",
            final_review_result="pass",
            next_owner="user",
        )
        specs = {
            "attempt_report_artifact": ("attempt.md", "attempt-report", "pass", 1),
            "last_review_artifact": ("preflight.md", "preflight-review", "pass", 2),
            "final_verification_artifact": ("verification.md", "final-verification", "pass", 3),
            "final_review_artifact": ("final-review.md", "final-review", "pass", 4),
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialize_schema5_lease(data if "data" in locals() else current, root)
            for key, (path, role, result, revision) in specs.items():
                target = root / path
                target.write_text(
                    schema5_evidence_manifest(role, result, current_batch=2, contract_revision=revision),
                    encoding="utf-8",
                )
                data[key] = {"path": path, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
            self.validator.validate_handoff_contract(data, "preflight-as-batch")
            with self.assertRaisesRegex(AssertionError, "evidence role|batch-review"):
                self.validator.validate_evidence_artifacts(data, root, "preflight-as-batch")

    def test_timeout_audit_is_blocked_only_and_cannot_satisfy_complete(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            timeout = root / "timeout.md"
            timeout.write_text(evidence_manifest("timeout-audit", "pass"), encoding="utf-8")
            shared = {"path": timeout.name, "sha256": hashlib.sha256(timeout.read_bytes()).hexdigest()}
            data.update(
                lifecycle_state="complete",
                current_batch=data["planned_batches"],
                attempt_report_artifact=dict(shared),
                last_review_result="pass",
                last_review_artifact=dict(shared),
                final_verification="pass",
                final_verification_artifact=artifact("verification.md"),
                final_review_result="pass",
                final_review_artifact=artifact("final-review.md"),
                next_owner="user",
            )
            with self.assertRaisesRegex(AssertionError, "timeout-audit|distinct|blocked"):
                self.validator.validate_handoff_contract(data, "timeout-complete")

    def test_runtime_rejects_stale_batch_and_attempt_evidence(self):
        data = self._awaiting_contract()
        data.update(attempt=9, contract_revision=10)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialize_schema5_lease(data if "data" in locals() else current, root)
            specs = {
                "attempt_report_artifact": ("report.md", "attempt-report", 1),
                "last_review_artifact": ("review.md", "batch-review", 2),
            }
            for key, (path, role, revision) in specs.items():
                target = root / path
                target.write_text(
                    schema5_evidence_manifest(role, "pass", current_batch=1, attempt=1, contract_revision=revision),
                    encoding="utf-8",
                )
                data[key] = {"path": path, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
            with self.assertRaisesRegex(AssertionError, "required batch|required attempt"):
                self.validator.validate_evidence_artifacts(data, root, "stale-evidence")

    def test_runtime_complete_requires_and_validates_previous_status(self):
        previous = self._awaiting_contract("pass")
        previous["contract_revision"] = 4
        current = dict(previous)
        current.update(
            lifecycle_state="complete",
            contract_revision=5,
            final_review_result="pass",
            final_review_artifact=artifact("final-review.md"),
            next_owner="user",
        )
        previous_bytes = b"canonical previous status revision 4\n"
        previous_sha = hashlib.sha256(previous_bytes).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialize_schema5_lease(data if "data" in locals() else current, root)
            specs = {
                "attempt_report_artifact": ("report.md", "attempt-report", "pass", 1, "b" * 64),
                "last_review_artifact": ("batch-review.md", "batch-review", "pass", 2, "c" * 64),
                "final_verification_artifact": ("verification.md", "final-verification", "pass", 3, "d" * 64),
                "final_review_artifact": ("final-review.md", "final-review", "pass", 4, previous_sha),
            }
            for key, (path, role, result, revision, source_sha) in specs.items():
                target = root / path
                target.write_text(
                    schema5_evidence_manifest(
                        role,
                        result,
                        current_batch=2,
                        contract_revision=revision,
                        canonical_sha256=source_sha,
                    ),
                    encoding="utf-8",
                )
                current[key] = {"path": path, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
            previous.update(
                attempt_report_artifact=current["attempt_report_artifact"],
                last_review_artifact=current["last_review_artifact"],
                final_verification_artifact=current["final_verification_artifact"],
            )
            with self.assertRaisesRegex(AssertionError, "requires previous canonical status"):
                self.validator.validate_evidence_artifacts(current, root, "complete-without-history")
            self.validator.validate_evidence_artifacts(
                current,
                root,
                "complete-with-history",
                previous=previous,
                previous_status_sha256=previous_sha,
            )

    def test_previous_status_binds_nonfinal_promotion_to_reviewed_attempt(self):
        previous = self.validator.extract_handoff_contract(self.handoff, "handoff")
        previous.update(
            lifecycle_state="ready-for-review",
            attempt=3,
            contract_revision=3,
            attempt_report_artifact=artifact("report.md"),
            next_owner="codex-brief-antigravity-review",
        )
        current = dict(previous)
        current.update(
            lifecycle_state="ready-for-brief",
            current_batch=2,
            attempt=1,
            contract_revision=4,
            last_review_result="pass",
            last_review_artifact=artifact("review.md"),
            next_owner="codex-brief-antigravity-review",
        )
        previous_sha = hashlib.sha256(b"reviewed attempt 3 status\n").hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialize_schema5_lease(data if "data" in locals() else current, root)
            report = root / "report.md"
            review = root / "review.md"
            report.write_text(
                schema5_evidence_manifest("attempt-report", "pass", attempt=2, contract_revision=1),
                encoding="utf-8",
            )
            review.write_text(
                schema5_evidence_manifest(
                    "batch-review",
                    "pass",
                    attempt=2,
                    contract_revision=3,
                    canonical_sha256=previous_sha,
                ),
                encoding="utf-8",
            )
            report_ref = {"path": report.name, "sha256": hashlib.sha256(report.read_bytes()).hexdigest()}
            review_ref = {"path": review.name, "sha256": hashlib.sha256(review.read_bytes()).hexdigest()}
            previous["attempt_report_artifact"] = report_ref
            current["attempt_report_artifact"] = report_ref
            current["last_review_artifact"] = review_ref
            with self.assertRaisesRegex(AssertionError, "wrong source attempt"):
                self.validator.validate_evidence_artifacts(
                    current,
                    root,
                    "wrong-attempt-promotion",
                    previous=previous,
                    previous_status_sha256=previous_sha,
                )

    def test_validator_honors_target_directory(self):
        missing = ROOT / "tests" / "definitely-missing-skill"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_templates.py"), str(missing)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn(str(missing), result.stdout + result.stderr)


    def _valid_lease(self):
        return {
            "decision_id": "decision-001",
            "artifact_revision": 2,
            "artifact_sha256": "a" * 64,
            "approved_scope": "approved source implementation",
            "approved_actions": ["run-safe-tests", "fix-review-finding"],
            "risk_profile": "standard",
            "decision_source": "ai-proposed/user-approved",
            "owner_instance_id": "codex-control-01",
            "status": "valid",
            "invalidation_conditions": ["scope-change", "risk-change", "user-correction"],
        }

    def _valid_review_evidence(self):
        return {
            "actual_diff_inspected": True,
            "production_wiring_trace": ["source -> transform -> runtime"],
            "critical_reruns": ["python3 -m unittest focused -v"],
            "independent_probe": {
                "kind": "adversarial",
                "command": "probe --bounded-input",
                "result": "pass",
            },
            "copy_fields": {
                "expected": ["id", "version"],
                "observed": ["id", "version"],
            },
            "claims": [{
                "claim": "restart recovery",
                "mechanism": "runner retry state machine",
                "evidence": "focused recovery probe",
            }],
        }

    def _schema5_contract(self):
        data = schema5_contract(self.validator, self.handoff)
        for key in (
            "executor_agent", "independent_reviewer_agent", "decision_owner",
        ):
            data.pop(key, None)
        data.update({
            "schema_version": 5,
            "control_plane_owner": {
                "agent_product": "codex",
                "agent_instance_id": "codex-control-01",
                "agent_role": "control-plane",
                "capability_profile": "control-plane-high",
            },
            "executor_assignment": {
                "agent_product": "codex",
                "agent_instance_id": "codex-executor-01",
                "agent_role": "executor",
                "capability_profile": "cohesive-medium",
            },
            "independent_reviewer_assignment": {
                "agent_product": "codex",
                "agent_instance_id": "codex-reviewer-01",
                "agent_role": "independent-reviewer",
                "capability_profile": "control-plane-high",
            },
            "decision_source": "ai-proposed/user-approved",
            "confirmation_lease": {
                "decision_id": "decision-001",
                "path": "docs/agent-collab/add-example-change/confirmation-lease.md",
                "sha256": "c" * 64,
            },
        })
        data["readonly_fields"] = list(self.validator.SCHEMA5_IMMUTABLE_FIELDS)
        return data

    def test_tiered_01_platform_permission_reuses_safe_command_lease(self):
        validate = getattr(self.validator, "validate_confirmation_lease", None)
        self.assertTrue(callable(validate), "Confirmation Lease behavior is not implemented")
        result = validate(self._valid_lease(), {
            "action": "run-safe-tests",
            "artifact_revision": 2,
            "artifact_sha256": "a" * 64,
            "scope": "approved source implementation",
            "risk_profile": "standard",
            "platform_authorized": True,
            "business_authorized": False,
        })
        self.assertEqual("reuse", result)

    def test_tiered_02_platform_permission_cannot_authorize_production_deletion(self):
        validate = getattr(self.validator, "validate_confirmation_lease", None)
        self.assertTrue(callable(validate), "layered authorization behavior is not implemented")
        with self.assertRaisesRegex(AssertionError, "business/production authorization"):
            validate(self._valid_lease(), {
                "action": "production-deletion",
                "artifact_revision": 2,
                "artifact_sha256": "a" * 64,
                "scope": "approved source implementation",
                "risk_profile": "strict",
                "platform_authorized": True,
                "business_authorized": False,
            })

    def test_tiered_03_ai_proposed_user_approved_provenance_is_preserved(self):
        validate = getattr(self.validator, "validate_decision_source", None)
        self.assertTrue(callable(validate), "decision provenance behavior is not implemented")
        self.assertEqual(
            "ai-proposed/user-approved",
            validate("ai-proposed/user-approved"),
        )
        with self.assertRaisesRegex(AssertionError, "decision_source"):
            validate("user-originated-from-ai-proposal")

    def test_tiered_04_mechanical_low_ambiguity_blocks_instead_of_designing(self):
        validate = getattr(self.validator, "validate_capability_action", None)
        self.assertTrue(callable(validate), "capability authority behavior is not implemented")
        self.assertEqual(
            "BLOCKED",
            validate("mechanical-low", "bounded-edit", ambiguity=True),
        )

    def test_tiered_05_high_review_detects_copy_field_loss_after_executor_pass(self):
        validate = getattr(self.validator, "validate_high_review_evidence", None)
        self.assertTrue(callable(validate), "High Review behavior is not implemented")
        evidence = self._valid_review_evidence()
        evidence["copy_fields"]["observed"] = ["id"]
        with self.assertRaisesRegex(AssertionError, "copy-field loss"):
            validate(evidence)

    def test_tiered_06_high_review_requires_independent_adversarial_probe(self):
        validate = getattr(self.validator, "validate_high_review_evidence", None)
        self.assertTrue(callable(validate), "independent probe behavior is not implemented")
        evidence = self._valid_review_evidence()
        evidence["independent_probe"] = None
        with self.assertRaisesRegex(AssertionError, "independent.*probe"):
            validate(evidence)

    def test_tiered_07_high_review_traces_claim_to_runtime_mechanism(self):
        validate = getattr(self.validator, "validate_high_review_evidence", None)
        self.assertTrue(callable(validate), "claim-to-mechanism behavior is not implemented")
        evidence = self._valid_review_evidence()
        evidence["claims"][0]["mechanism"] = ""
        with self.assertRaisesRegex(AssertionError, "claim-to-mechanism"):
            validate(evidence)

    def test_tiered_08_same_product_instances_cannot_self_review(self):
        contract = self._schema5_contract()
        self.validator.validate_legacy_handoff_contract(
            contract, "same-product-distinct-instance"
        )
        contract["independent_reviewer_assignment"]["agent_instance_id"] = "codex-executor-01"
        with self.assertRaisesRegex(AssertionError, "instance"):
            self.validator.validate_legacy_handoff_contract(
                contract, "same-instance-self-review"
            )

    def test_tiered_09_single_correction_creates_candidate_without_promotion(self):
        evaluate = getattr(self.validator, "evaluate_learning_candidate", None)
        self.assertTrue(callable(evaluate), "Learning Candidate behavior is not implemented")
        result = evaluate({
            "severity": "low",
            "scope": "task-local",
            "independent_reproductions": 1,
            "event_kind": "wording-correction",
        })
        self.assertTrue(result["candidate_created"])
        self.assertFalse(result["proposal_allowed"])
        self.assertFalse(result["implementation_allowed"])

    def test_tiered_10_high_severity_candidate_is_proposal_only_without_approval(self):
        evaluate = getattr(self.validator, "evaluate_learning_candidate", None)
        self.assertTrue(callable(evaluate), "Learning Candidate promotion behavior is not implemented")
        result = evaluate({
            "severity": "high",
            "scope": "global",
            "independent_reproductions": 1,
            "event_kind": "false-pass",
            "openspec_approval": False,
        })
        self.assertTrue(result["proposal_allowed"])
        self.assertFalse(result["implementation_allowed"])


    def _lease_artifact_text(
        self, owner_instance_id="codex-control-01", risk_profile="standard",
        decision_source="ai-proposed/user-approved",
    ):
        return (
            "<!-- COOP_CONFIRMATION_LEASE_START -->\n"
            "```yaml\n"
            "decision_id: decision-001\n"
            "artifact_revision: 2\n"
            f"artifact_sha256: {'a' * 64}\n"
            "approved_scope: approved source implementation\n"
            "approved_actions:\n"
            "  - run-safe-tests\n"
            f"risk_profile: {risk_profile}\n"
            f"decision_source: {decision_source}\n"
            f"owner_instance_id: {owner_instance_id}\n"
            "status: valid\n"
            "invalidation_conditions:\n"
            "  - scope-change\n"
            "```\n"
            "<!-- COOP_CONFIRMATION_LEASE_END -->\n"
        )

    def test_schema5_runtime_validates_confirmation_lease_artifact(self):
        validate = getattr(
            self.validator, "_validate_legacy_confirmation_lease_artifact", None
        )
        self.assertTrue(callable(validate), "runtime lease artifact validation is not implemented")
        data = self._schema5_contract()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / data["confirmation_lease"]["path"]
            target.parent.mkdir(parents=True)
            target.write_text(self._lease_artifact_text(), encoding="utf-8")
            data["confirmation_lease"]["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
            validate(data, root, "valid-lease")
            target.write_text(self._lease_artifact_text("wrong-owner"), encoding="utf-8")
            data["confirmation_lease"]["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
            with self.assertRaisesRegex(AssertionError, "owner_instance_id"):
                validate(data, root, "wrong-owner")
            target.write_text(self._lease_artifact_text(risk_profile="strict"), encoding="utf-8")
            data["confirmation_lease"]["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
            with self.assertRaisesRegex(AssertionError, "risk_profile"):
                validate(data, root, "wrong-risk")
            target.write_text(self._lease_artifact_text(decision_source="revoked"), encoding="utf-8")
            data["confirmation_lease"]["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
            with self.assertRaisesRegex(AssertionError, "revoked|valid"):
                validate(data, root, "revoked-lease")

    def test_schema5_high_review_artifact_requires_mechanism_sections(self):
        validate = getattr(self.validator, "validate_high_review_artifact_text", None)
        self.assertTrue(callable(validate), "runtime High Review artifact validation is not implemented")
        incomplete = schema5_evidence_manifest("batch-review", "pass", high_review=False)
        with self.assertRaisesRegex(AssertionError, "actual diff|production wiring|claim-to-mechanism|independent"):
            validate(incomplete, "incomplete-review")
        complete = incomplete + (
            "\nActual files and complete diff inspected\n"
            "Copy/transform/production wiring trace\n"
            "Critical reruns\n"
            "Claim-to-mechanism support\n"
            "Independent adversarial probe\n"
        )
        validate(complete, "complete-review")

    def test_schema4_inventory_blocks_active_and_allows_complete_history(self):
        inventory = getattr(self.validator, "inventory_active_schema4_statuses", None)
        self.assertTrue(callable(inventory), "schema-4 drain inventory is not implemented")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            status = root / "docs" / "agent-collab" / "legacy" / "status.md"
            status.parent.mkdir(parents=True)
            active = schema4_contract(
                self.validator,
                self.handoff,
                lifecycle_state="ready-for-execution",
                next_owner="external-agent",
            )
            status.write_text(
                render_handoff_contract(self.validator, active), encoding="utf-8"
            )
            self.assertEqual([status.resolve()], inventory([root]))

            complete = schema4_contract(
                self.validator,
                self.handoff,
                lifecycle_state="complete",
                current_batch=2,
                last_review_result="pass",
                final_verification="pass",
                final_review_result="pass",
                attempt_report_artifact=artifact("report.md"),
                last_review_artifact=artifact("review.md"),
                final_verification_artifact=artifact("verification.md"),
                final_review_artifact=artifact("final-review.md"),
                next_owner="user",
            )
            status.write_text(
                render_handoff_contract(self.validator, complete), encoding="utf-8"
            )
            self.assertEqual([], inventory([root]))


    def test_schema5_revoked_lease_blocks_and_cannot_be_reactivated(self):
        before = self._schema5_contract()
        before["confirmation_lease_status"] = "valid"
        after = dict(before)
        after.update(
            lifecycle_state="blocked",
            contract_revision=before["contract_revision"] + 1,
            last_review_result="blocked",
            last_review_artifact=artifact("docs/review/revoked-lease.md"),
            blocked_reason="user revoked the prior decision",
            blocker_owner="user",
            resume_condition="create a new explicitly authorized contract and Lease",
            next_owner="user",
            confirmation_lease_status="revoked",
        )
        self.validator._validate_legacy_transition(before, after, "revoke-lease")
        recovered = dict(after)
        recovered.update(
            lifecycle_state="ready-for-execution",
            contract_revision=after["contract_revision"] + 1,
            attempt=after["attempt"] + 1,
            last_review_result="not-run",
            last_review_artifact=None,
            blocked_reason=None,
            blocker_owner="none",
            resume_condition=None,
            next_owner="external-agent",
            confirmation_lease_status="valid",
        )
        with self.assertRaisesRegex(AssertionError, "revoked|new.*Lease|reactivat"):
            self.validator._validate_legacy_transition(
                after, recovered, "reactivate-old-lease"
            )


if __name__ == "__main__":
    unittest.main()
