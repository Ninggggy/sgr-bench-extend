"""Validate the explicit stage schema and materialize non-blind inline files.

No external dependency is required. Unsupported schema keywords fail closed.
Only the small JSON Schema vocabulary used by this pipeline is supported.
"""
import json
from pathlib import Path, PurePosixPath


def validate(value, schema, path='$'):
    supported = {'$schema', 'title', 'description', 'type', 'additionalProperties',
                 'properties', 'required', 'items', 'enum', 'const', 'anyOf',
                 'minLength', 'maxLength', 'minItems', 'maxItems', 'minimum', 'maximum'}
    if set(schema) - supported:
        raise ValueError(f'{path}: unsupported schema keywords {set(schema)-supported}')
    if 'anyOf' in schema:
        for branch in schema['anyOf']:
            try:
                validate(value, branch, path)
                break
            except ValueError:
                pass
        else:
            raise ValueError(f'{path}: no anyOf branch matches')
    kinds = {'object': lambda v: isinstance(v, dict), 'array': lambda v: isinstance(v, list),
             'string': lambda v: isinstance(v, str), 'integer': lambda v: type(v) is int,
             'number': lambda v: type(v) in (int, float), 'boolean': lambda v: type(v) is bool,
             'null': lambda v: v is None}
    if 'type' in schema:
        allowed = schema['type'] if isinstance(schema['type'], list) else [schema['type']]
        if not any(kinds[k](value) for k in allowed):
            raise ValueError(f'{path}: wrong type')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'{path}: value not in enum')
    if 'const' in schema and value != schema['const']:
        raise ValueError(f'{path}: wrong constant')
    if isinstance(value, dict):
        if set(schema.get('required', [])) - set(value):
            raise ValueError(f'{path}: missing required fields')
        properties = schema.get('properties', {})
        if schema.get('additionalProperties') is False and set(value)-set(properties):
            raise ValueError(f'{path}: unexpected fields')
        for key, child in value.items():
            if key in properties:
                validate(child, properties[key], path+'.'+key)
    if isinstance(value, list):
        for i, child in enumerate(value):
            if 'items' in schema:
                validate(child, schema['items'], f'{path}[{i}]')
    for key, check in [('minLength', lambda: len(value) >= schema[key]),
                       ('maxLength', lambda: len(value) <= schema[key]),
                       ('minItems', lambda: len(value) >= schema[key]),
                       ('maxItems', lambda: len(value) <= schema[key]),
                       ('minimum', lambda: value >= schema[key]),
                       ('maximum', lambda: value <= schema[key])]:
        if key in schema and not check():
            raise ValueError(f'{path}: {key} failed')


def materialize_files(result, destination, *, write=True, registered_data=None):
    """Inline files are actual content, never a claim that an inaccessible path exists."""
    destination = Path(destination)
    files = result.get('files', [])
    if not isinstance(files, list):
        raise ValueError('files must be an array')
    seen, validated = set(), []
    for item in files:
        if not isinstance(item, dict) or set(item) != {'path', 'content'}:
            raise ValueError('Each inline file needs exactly path and content')
        name, content = item['path'], item['content']
        if not isinstance(name, str) or not name or not isinstance(content, str):
            raise ValueError('Invalid inline file')
        parts = PurePosixPath(name)
        if parts.is_absolute() or '..' in parts.parts or '\\' in name or str(parts) != name:
            raise ValueError('Unsafe or noncanonical asset path')
        if name in seen:
            raise ValueError('Duplicate inline file path')
        seen.add(name)
        target = destination / name
        if not target.resolve().is_relative_to(destination.resolve()):
            raise ValueError('Asset path escapes output directory')
        if target.suffix == '.json':
            json.loads(content)
        elif target.suffix == '.py':
            compile(content, name, 'exec')
        validated.append((target, content))
    external = []
    registry = {}
    if registered_data is not None:
        registered_data = Path(registered_data).resolve()
        registry_path = registered_data / 'registry.json'
        if registry_path.is_file():
            registry = json.loads(registry_path.read_text())
    for artifact in result.get('artifacts', []):
        if artifact['path'] not in seen:
            entry = registry.get(artifact['path'])
            if not isinstance(entry, dict) or not isinstance(entry.get('path'), str):
                raise ValueError('Declared artifact missing actual inline content: '+artifact['path'])
            relative = PurePosixPath(entry['path'])
            target = registered_data / relative
            if (relative.is_absolute() or '..' in relative.parts or '\\' in entry['path']
                    or str(relative) != entry['path'] or target.is_symlink()
                    or not target.resolve().is_relative_to(registered_data)
                    or not target.is_file() or target.stat().st_size == 0):
                raise ValueError('Invalid recovered registered artifact: '+artifact['path'])
            external.append({'file_id':artifact['path'], 'registered_path':entry['path'],
                             'bytes':target.stat().st_size})
    if write:
        destination.mkdir(exist_ok=True)
        for target, content in validated:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise ValueError('Refusing to overwrite an existing stage asset')
            target.write_text(content)
    else:
        for target, content in validated:
            if not target.is_file() or target.read_text() != content:
                raise ValueError('Recovered asset differs from result content')
    return [{'path':str(target.relative_to(destination)), 'bytes':len(content.encode())}
            for target, content in validated] + external
