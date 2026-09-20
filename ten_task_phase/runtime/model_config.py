"""Future blind-run defaults and checks against recorded runtime evidence.

No model calls are made here. Historical runs are verified against their own
requested settings, never against the current defaults.
"""
import json
import re
import tomllib

BLIND_MODEL = 'gpt-5.6-sol'
BLIND_EFFORT = 'medium'
AUDIT_MODEL = 'gpt-6-astra'
AUDIT_EFFORT = 'medium'
EFFORTS = ('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra')


def tool_profile_config(template, role, profile='standard'):
    """Web-only and public-web blind profiles remove data MCP servers; keep isolation."""
    if profile not in ('standard', 'web_only', 'public_web'):
        raise ValueError('Unknown blind tool profile')
    if role != 'blind' or profile == 'standard':
        return template
    before = tomllib.loads(template)
    lines, skip = [], False
    for line in template.splitlines(keepends=True):
        if line.lstrip().startswith('['):
            skip = bool(re.match(r'^\s*\[\[?mcp_servers(?:\.|\])', line))
        if not skip:
            lines.append(line)
    result = ''.join(lines)
    expected = {k: v for k, v in before.items() if k != 'mcp_servers'}
    if tomllib.loads(result) != expected:
        raise ValueError('Web-only transformation altered other settings')
    return result


def select_model(model=None, effort=None, *, audit=False):
    chosen_model = model if model is not None else AUDIT_MODEL if audit else BLIND_MODEL
    chosen_effort = effort if effort is not None else AUDIT_EFFORT if audit else BLIND_EFFORT
    if not isinstance(chosen_model, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]*', chosen_model):
        raise ValueError('Model must be a nonempty model identifier')
    if chosen_effort not in EFFORTS:
        raise ValueError('Unsupported reasoning effort value')
    if audit and (chosen_model != AUDIT_MODEL or chosen_effort not in (AUDIT_EFFORT, 'high')):
        raise ValueError('Construction and private-asset audits require gpt-6-astra with medium or explicitly requested high')
    return chosen_model, chosen_effort


def render_config(template, model, effort):
    """Replace only two top-level settings; preserve provider, tools and sandbox."""
    before = tomllib.loads(template)
    if not all(isinstance(before.get(k), str) for k in ('model', 'model_reasoning_effort')):
        raise ValueError('Template must explicitly declare model and model_reasoning_effort')
    replacements = {'model': model, 'model_reasoning_effort': effort}
    replaced = set()
    lines = []
    in_table = False
    for line in template.splitlines(keepends=True):
        if line.lstrip().startswith('['):
            in_table = True
        match = None if in_table else re.match(r'^(\s*)(model|model_reasoning_effort)(\s*=\s*).*?(\r?\n)?$', line)
        if match:
            key = match.group(2)
            lines.append(match.group(1) + key + match.group(3) + json.dumps(replacements[key]) + (match.group(4) or ''))
            replaced.add(key)
        else:
            lines.append(line)
    if replaced != set(replacements):
        raise ValueError('Cannot safely replace the template model settings')
    rendered = ''.join(lines)
    if tomllib.loads(rendered) != {**before, **replacements}:
        raise ValueError('Rendering changed other configuration settings')
    return rendered
