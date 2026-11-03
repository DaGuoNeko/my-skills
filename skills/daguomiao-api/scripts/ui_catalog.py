# -*- coding: utf-8 -*-
"""Live index of DAGUOMIAO_API_MOD public UI, read straight from the pre-mod source.

python ui_catalog.py [--root PATH] list [关键词]   公共控件：名称、继承、参数数、子控件
python ui_catalog.py [--root PATH] show 控件名      一个控件的参数默认值、子控件、引用贴图
python ui_catalog.py [--root PATH] raw 控件名       一个控件的原始 JSON
python ui_catalog.py [--root PATH] textures [关键词] 前置 UI 贴图清单
python ui_catalog.py [--root PATH] screens          前置自带界面（同风格样板）
python ui_catalog.py [--root PATH] selftest         用当前源码自检
"""
import io
import json
import os
import subprocess
import sys

DEFAULT_ROOT = r'C:\Users\cat\Desktop\DAGUOMIAO_API_MOD\DAGUOMIAO_API_MOD'
NS = 'DAGUOMIAO_API_MOD'


def paths(root):
    res = os.path.join(root, NS + 'R')
    return os.path.join(res, 'ui'), os.path.join(res, 'textures', 'ui', NS)


def load(path):
    with io.open(path, encoding='utf-8') as f:
        return json.load(f)


def controls(root):
    """{name: (base, body)} for top-level controls of the common file; keys look like 'name@base'."""
    data = load(os.path.join(paths(root)[0], NS + '_common.json'))
    out = {}
    for key, body in data.items():
        if key == 'namespace' or not isinstance(body, dict):
            continue
        name, _, base = key.partition('@')
        out[name] = (base, body)
    return out


def params(body):
    return {k: v for k, v in body.items() if k.startswith('$')}


def children(body):
    names = []
    for item in body.get('controls', []):
        if isinstance(item, dict):
            names.extend(k for k in item)
    return names


def textures_used(node, found=None):
    found = set() if found is None else found
    if isinstance(node, dict):
        for v in node.values():
            textures_used(v, found)
    elif isinstance(node, list):
        for v in node:
            textures_used(v, found)
    elif isinstance(node, str) and ('textures/' in node or 'UiTexturesPath' in node):
        found.add(node)
    return found


def version(root):
    try:
        return subprocess.check_output(['git', '-C', root, 'log', '-1', '--format=%h %cd', '--date=short'],
                                       stderr=subprocess.DEVNULL).decode('utf-8').strip()
    except Exception:
        return 'unknown'


def cmd_list(root, kw=''):
    print('# %s_common @ %s' % (NS, version(root)))
    for name, (base, body) in sorted(controls(root).items(), key=lambda x: x[0].lower()):
        if kw.lower() in name.lower():
            print('%-40s @%-42s $%-3d children: %s' % (name, base or '-', len(params(body)), ', '.join(children(body))[:80]))


def cmd_show(root, name):
    ctl = controls(root)
    if name not in ctl:
        sys.exit('no control %r; try: list %s' % (name, name[:4]))
    base, body = ctl[name]
    print('%s@%s  type=%s' % (name, base or '-', body.get('type', '(inherited)')))
    parent = base.replace(NS + '_common.', '')
    if parent in ctl:
        print('inherits params/children from %r: run  show %s' % (parent, parent))
    print('params (override with $name, defaults shown):')
    for k, v in sorted(params(body).items()):
        print('  %-40s %s' % (k, json.dumps(v, ensure_ascii=False)))
    print('children: %s' % ', '.join(children(body)))
    print('textures: %s' % ', '.join(sorted(textures_used(body))))


def cmd_raw(root, name):
    ctl = controls(root)
    if name not in ctl:
        sys.exit('no control %r' % name)
    print(json.dumps(ctl[name][1], ensure_ascii=False, indent=2))


def cmd_textures(root, kw=''):
    tex_dir = paths(root)[1]
    for dirpath, _, files in os.walk(tex_dir):
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(dirpath, f), tex_dir).replace(os.sep, '/')
            if f.endswith('.png') and kw.lower() in rel.lower():
                print('($%s_UiTexturesPath + \'/%s\')' % (NS, rel[:-4]))


def cmd_screens(root):
    ui = paths(root)[0]
    for f in sorted(os.listdir(ui)):
        if f.endswith('_screen.json'):
            tops = [k for k in load(os.path.join(ui, f)) if k != 'namespace']
            print('%-55s %s' % (f, ', '.join(tops)))


def cmd_selftest(root):
    ctl = controls(root)
    assert 'newbutt2' in ctl and params(ctl['newbutt2'][1]), 'newbutt2 missing or has no params'
    assert ctl['newbutt2'][0] == 'common.button', ctl['newbutt2'][0]
    assert any(f.endswith('.png') for _, _, fs in os.walk(paths(root)[1]) for f in fs), 'no textures'
    assert any(f.endswith('_screen.json') for f in os.listdir(paths(root)[0])), 'no screens'
    print('ok: %d controls, version %s' % (len(ctl), version(root)))


def main(argv):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    root = DEFAULT_ROOT
    if argv[:1] == ['--root']:
        root, argv = argv[1], argv[2:]
    if not os.path.isdir(paths(root)[0]):
        sys.exit('pre-mod UI not found under %r; pass --root <DAGUOMIAO_API_MOD repo>' % root)
    cmd, args = (argv[0], argv[1:]) if argv else ('list', [])
    handlers = {'list': cmd_list, 'show': cmd_show, 'raw': cmd_raw, 'textures': cmd_textures,
                'screens': cmd_screens, 'selftest': cmd_selftest}
    if cmd not in handlers:
        sys.exit(__doc__)
    handlers[cmd](root, *args)


if __name__ == '__main__':
    main(sys.argv[1:])
