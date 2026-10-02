"""Check the admission ordering statements without rerunning native production."""
import ast
import copy
from pathlib import Path


def main():
    source = Path(__file__).with_name('admit-c130-native-ledger-v1.py')
    tree = ast.parse(source.read_text(encoding='utf-8'))
    body = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main').body
    start = next(i for i, node in enumerate(body)
                 if isinstance(node, ast.Assign)
                 and any(isinstance(target, ast.Name) and target.id == 'matches' for target in node.targets))
    assert isinstance(body[start + 1], ast.Assert) and isinstance(body[start + 2], ast.If)
    code = compile(ast.Module(body=body[start:start + 3], type_ignores=[]), str(source), 'exec')
    replacement = {'root': 'target', 'documents': ['new']}
    prior = [{'root': 'before'}, {'root': 'target', 'documents': ['old']}, {'root': 'after'}]
    nav = {'course_surfaces': copy.deepcopy(prior)}

    def run():
        exec(code, {'nav': nav, 'SITE': 'target', 'surface': replacement})

    run()
    assert nav['course_surfaces'] == [prior[0], replacement, prior[2]]
    run()
    assert nav['course_surfaces'] == [prior[0], replacement, prior[2]]
    nav = {'course_surfaces': [prior[0], prior[2]]}
    run()
    assert nav['course_surfaces'] == [prior[0], prior[2], replacement]
    nav = {'course_surfaces': [replacement, replacement]}
    try:
        run()
    except AssertionError:
        pass
    else:
        raise AssertionError('Duplicate native surface accepted')
    print('PASS: preserve position, idempotent replay, append absent, reject duplicate')


if __name__ == '__main__':
    main()
