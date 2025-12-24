
"""Utility functions for NMAgents."""

import json
import re
import yaml
from typing import Any
import logging as log
from nmagents.command import CallLLM,ToolCall

def extract_code_blocks(text: str) -> list[str]:
    # Match ```lang (optional) ... ``` with DOTALL so newlines are included.
    pattern = r"```(?:\w+\n)?(.*?)```"
    return [block.strip() for block in re.findall(pattern, text, re.S)]


def parse_json_response_with_repair(
    response_text: str,
    *,
    schema_hint: str | None,
    repair_command: CallLLM | None,
    context_label: str,
) -> tuple[dict[str, Any], str]:
    """
    Try to parse the response as JSON; if that fails, ask a cheaper model
    to repair the payload so it conforms to the expected schema.
    """
    code_blocks = extract_code_blocks(response_text)
    json_payload = code_blocks[0] if code_blocks else response_text
    try:
        data = json.loads(json_payload)
        return data or {}, json_payload
    except json.JSONDecodeError as exc:
        log.error("%s: JSON parse failed: %s", json_payload, exc)
        # If the model returned YAML-shaped content, try parsing it leniently
        # before invoking the repair model.
        try:
            yaml_data = yaml.safe_load(json_payload)
            if isinstance(yaml_data, (dict, list)):
                log.info("%s: parsed fallback YAML after JSON failure", context_label)
                return yaml_data or {}, json_payload
        except yaml.YAMLError:
            pass
        if repair_command is None:
            raise
        repair_prompt_parts = [
            "You are given JSON content that failed to parse. "
            "Return corrected JSON that matches the expected schema.",
        ]
        if schema_hint:
            repair_prompt_parts.append(
                "The schema or template to follow is:\n"
                f"{schema_hint}\n"
            )
        repair_prompt_parts.append(
            "Broken JSON:\n```json\n"
            f"{json_payload}\n"
            "```\n"
            f"Parser error: {exc}\n"
            "Return only the fixed JSON inside a single ```json``` block."
        )
        repair_prompt = "\n".join(repair_prompt_parts)
        log.info(
            "%s: attempting JSON repair with model %s",
            context_label,
            repair_command.model,
        )
        repair_response = repair_command.execute(repair_prompt)
        repair_blocks = extract_code_blocks(repair_response or "")
        repaired_payload = repair_blocks[0] if repair_blocks else repair_response
        try:
            data = json.loads(repaired_payload)
            return data or {}, repaired_payload
        except json.JSONDecodeError as repair_exc:
            raise ValueError(
                f"{context_label}: failed to repair JSON; "
                f"original error: {exc}; repair error: {repair_exc}"
            ) from repair_exc


def _collect_tool_specs(step: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a normalized list of tool payloads embedded in a plan step."""
    tool_specs: list[dict[str, Any]] = []

    raw_tools = step.get("tools")
    if isinstance(raw_tools, dict):
        tool_specs.append(raw_tools)
    elif isinstance(raw_tools, list):
        for item in raw_tools:
            if isinstance(item, dict):
                tool_specs.append(item)
            else:
                log.warning("Ignoring non-dict entry in 'tools': %r", item)
    return tool_specs


def _build_tool_call_payload(tool_spec: dict[str, Any]) -> dict[str, Any]:
    """Convert a tool spec into the JSON payload expected by ToolCall."""
    if not isinstance(tool_spec, dict):
        raise ValueError("tool specification must be a mapping")

    parameters = tool_spec.get("parameters")
    if parameters is None:
        excluded_keys = {
            "name",
            "server",
            "tool",
            "function",
            "function_name",
            "method",
            "description",
            "parameters",
        }
        parameters = {k: v for k, v in tool_spec.items()
                      if k not in excluded_keys}

    if not isinstance(parameters, dict):
        raise ValueError("tool parameters must be a mapping")

    method = (
        tool_spec.get("function")
        or tool_spec.get("method")
        or tool_spec.get("function_name")
    )
    if not method:
        raise ValueError(
            "tool specification missing 'function' or 'method' key")

    payload: dict[str, Any] = {"method": method, "params": parameters}

    server = tool_spec.get("server") or tool_spec.get("name")
    if isinstance(server, str) and server:
        payload["server"] = server

    return payload


async def execute_step_tools(
    step: dict[str, Any],
    tool_command: ToolCall,
) -> list[str]:
    """Invoke any MCP tools declared in the step and return their outputs."""
    tool_outputs: list[str] = []
    tool_specs = _collect_tool_specs(step)
    if not tool_specs:
        log.debug("No tools declared for step %s",
                  step.get("name", "<unnamed>"))
        return tool_outputs

    for tool_spec in tool_specs:
        try:
            payload = _build_tool_call_payload(tool_spec)
        except ValueError as exc:
            log.warning(
                "Skipping tool execution for step %s: %s",
                step.get("name", "<unnamed>"),
                exc,
            )
            continue

        payload_json = json.dumps(payload)
        log.info(
            "Executing MCP tool '%s' with params %s",
            payload["method"],
            payload["params"],
        )
        tool_result, succeeded = await tool_command.execute(payload_json)
        log.info(
            "Tool call %s for '%s'",
            "succeeded" if succeeded else "failed",
            payload["method"],
        )
        tool_outputs.append(tool_result)
    return tool_outputs