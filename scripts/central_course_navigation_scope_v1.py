"""Closed cross-role boundaries for nested readers and their course tools."""
from pathlib import Path, PurePosixPath


def safe_relative(value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('navigation path must be nonempty relative POSIX text')
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ('', '.', '..') for p in value.split('/')) or ':' in value:
        raise ValueError('navigation path must be normalized and relative')
    return path


def course_surface_exclusions(surface, contract):
    values = surface.get('exclude_subtrees', [])
    if not isinstance(values, list) or len(values) != len(set(values)):
        raise ValueError('course-surface exclusions must be a unique list')
    readers = {r['root']: r for r in contract['readers']}
    surfaces = {s['root']: s for s in contract['course_surfaces']}
    if len(surfaces) != len(contract['course_surfaces']):
        raise ValueError('course-surface roots must be unique')
    course_ids = {c for d in surface['documents'] for c in d['course_ids']}
    root = safe_relative(surface['root'])
    for value in values:
        target = (root / safe_relative(value)).as_posix()
        reader_matches = target in readers and readers[target]['course_id'] in course_ids
        child = surfaces.get(target)
        child_matches = child is not None and bool(child['documents']) and {
            c for d in child['documents'] for c in d['course_ids']
        } == course_ids
        if not reader_matches and not child_matches:
            raise ValueError('a course-surface exclusion must be an exact registered reader or child surface of the same course')
    return values


def reader_course_targets(reader, contract, workspace):
    values = reader.get('related_course_surface_paths', [])
    if not isinstance(values, list) or len(values) != len(set(values)):
        raise ValueError('reader course links must be a unique list')
    declared = {
        (safe_relative(s['root']) / safe_relative(d['path'])).as_posix(): d
        for s in contract['course_surfaces'] for d in s['documents']
    }
    result = []
    for value in values:
        safe_relative(value)
        if value not in declared or reader['course_id'] not in declared[value]['course_ids']:
            raise ValueError('reader return must target a declared tool for the same course')
        result.append((Path(workspace) / value).resolve())
    return result


def course_surface_targets(surface, document, contract, workspace):
    """Resolve explicit cross-surface links without weakening local contents closure."""
    values = document.get('related_course_surface_paths', [])
    if not isinstance(values, list) or len(values) != len(set(values)):
        raise ValueError('course-surface related links must be a unique list')
    declared = {
        (safe_relative(s['root']) / safe_relative(d['path'])).as_posix(): d
        for s in contract['course_surfaces'] for d in s['documents']
    }
    source = (safe_relative(surface['root']) / safe_relative(document['path'])).as_posix()
    course_ids = set(document['course_ids'])
    result = []
    for value in values:
        safe_relative(value)
        if value == source or value not in declared or set(declared[value]['course_ids']) != course_ids:
            raise ValueError('course-surface return must target another declared tool for the same course set')
        target = (Path(workspace) / value).resolve()
        if not target.is_relative_to((Path(workspace) / 'docs').resolve()) or not target.is_file():
            raise ValueError('course-surface return must target an existing declared document below docs')
        result.append(target)
    return result
