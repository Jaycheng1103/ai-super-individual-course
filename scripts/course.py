#!/usr/bin/env python3
"""Course setup helper. Standard library only; never executes downloaded code."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'sources.lock.json'
AGENTS = {'codex': '.agents/skills', 'claude-code': '.claude/skills'}
COURSE = json.loads((ROOT / 'course-map.json').read_text(encoding='utf-8'))
STEPS = [s['id'] for s in COURSE['stages']]
LEGACY = dict(zip([f'{i:02}' for i in range(13)],
                  ['environment', 'workspace', 'background', 'connectors', 'knowledge',
                   'skills', 'research', 'editor', 'transcription', 'first-video', 'service', 'delivery', 'optional']))
MAX_ARCHIVE = 150 * 1024 * 1024
MAX_EXPANDED = 300 * 1024 * 1024


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def workspace(value, existing=True):
    p = Path(value).expanduser().resolve()
    if p == ROOT or ROOT in p.parents:
        raise ValueError('學員資料不可寫進課程 repo 或其子目錄。教材可放在私人專案內的獨立子目錄。')
    if existing and not (p / '.course/progress.json').is_file():
        raise ValueError('這不是本工具建立的學員工作區。已有第二大腦請依 docs/existing-workspace.md 手動接入。')
    if existing and p not in (p / '.course').resolve().parents:
        raise ValueError('學習進度目錄不可連結到工作區外。')
    return p


def safe_extract(archive, dest):
    """Strip GitHub's one root directory, reject traversal, skip symlinks."""
    with tarfile.open(archive, 'r:gz') as t:
        members = t.getmembers()
        if len(members) > 15000 or sum(m.size for m in members) > MAX_EXPANDED:
            raise ValueError('來源包超出預期大小，停止解壓。')
        roots = {PurePosixPath(m.name).parts[0] for m in members if m.name}
        if len(roots) != 1:
            raise ValueError('來源包不是單一 GitHub 根目錄。')
        for m in members:
            p = PurePosixPath(m.name)
            if p.is_absolute() or '..' in p.parts or '\\' in m.name or ':' in m.name:
                raise ValueError('來源包包含不安全路徑。')
            rel = Path(*p.parts[1:])
            if not rel.parts:
                continue
            target = dest / rel
            if dest.resolve() not in target.resolve().parents:
                raise ValueError('來源路徑超出目的地。')
            if m.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif m.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                with t.extractfile(m) as src, target.open('wb') as out:
                    shutil.copyfileobj(src, out)
            elif m.issym() or m.islnk():
                # Selected teaching packages do not depend on upstream root aliases.
                continue
            else:
                raise ValueError('來源包包含特殊檔案，停止。')


def fetch(source_id, temp, cache=None):
    sources = json.loads(LOCK.read_text(encoding='utf-8'))['sources']
    s = sources[source_id]
    archive = temp / (source_id + '.tar.gz')
    cached = Path(cache) / (s['repo'].replace('/', '__') + '.tar.gz') if cache else None
    if cached and cached.is_file():
        shutil.copyfile(cached, archive)
    else:
        request = urllib.request.Request(s['archive_url'], headers={'User-Agent': 'AI-Course-Setup/1.0'})
        count = 0
        with urllib.request.urlopen(request, timeout=60) as response, archive.open('wb') as f:
            while True:
                data = response.read(1024 * 1024)
                if not data:
                    break
                count += len(data)
                if count > MAX_ARCHIVE:
                    raise ValueError('下載超過大小上限。')
                f.write(data)
    if digest(archive) != s['archive_sha256']:
        raise ValueError('來源 SHA-256 與教材鎖定版本不同，停止；請聯絡講師更新，不要跳過驗證。')
    dest = temp / source_id
    dest.mkdir()
    safe_extract(archive, dest)
    return dest, s


def fingerprints(folder):
    return {str(p.relative_to(folder)).replace(os.sep, '/'): digest(p)
            for p in sorted(folder.rglob('*')) if p.is_file()}


def new_progress():
    return {'schema': 2, 'course_version': COURSE['version'],
            'created_at': datetime.now(timezone.utc).isoformat(), 'course_repo': str(ROOT),
            'workspace_state': 'prepared',
            'steps': {s: {'status': 'pending', 'evidence': ''} for s in STEPS}}


def start(args):
    target = workspace(args.workspace, existing=False)
    if target.exists():
        raise ValueError('目的地已存在；start 只建立全新私人學習資料夾。既有庫請使用手動接入流程。')
    target.mkdir(parents=True)
    write_json(target / '.course/progress.json', new_progress())
    return {'workspace': str(target), 'status': 'prepared',
            'next': '這是尚無專案時的備用流程；筆記先放 .course，再初始化 AIS-OS。'}


def load_progress(path):
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('schema') not in (None, 1, 2):
        raise ValueError('未知進度格式，保留原檔並停止，不降版或重建。')
    if data.get('schema') != 2:
        # Preserve the exact old record once. New acceptance criteria require review,
        # not automatically re-installing anything that already works.
        backup = path.with_name('progress.v1.backup.json')
        if not backup.exists():
            with backup.open('x', encoding='utf-8') as f:
                f.write(path.read_text(encoding='utf-8'))
        previous = data.get('steps', {})
        data['steps'] = {s: {'status': 'pending', 'evidence': ''} for s in STEPS}
        for old, record in previous.items():
            key = LEGACY.get(old, old)
            if key in data['steps']:
                data['steps'][key] = {**record, 'status': 'needs_review',
                                      'previous_status': record.get('status', 'pending'),
                                      'next_action': '核對新版驗收；保留已完成作品與設定，不重新安裝。'}
        data.update(schema=2, course_version=COURSE['version'])
        write_json(path, data)
    if data.get('course_version') != COURSE['version'] or set(data['steps']) != set(STEPS):
        raise ValueError('進度版本與教材不符；先保留原進度並比對教材，不自動丟棄記錄。')
    return data


def init(args):
    target = workspace(args.workspace, existing=False)
    prepared = None
    in_place = getattr(args, 'in_place', False)
    if in_place and (target == Path.home().resolve() or target == Path(target.anchor)):
        raise ValueError('請選課程專用專案，不能在使用者家目錄或磁碟根目錄初始化。')
    if in_place and not target.is_dir():
        raise ValueError('--in-place 只用於目前已存在的專案資料夾。')
    if target.exists():
        if target.is_dir() and {p.name for p in target.iterdir()} == {'.course'}:
            ws = workspace(str(target))
            prepared = load_progress(ws / '.course/progress.json')
        if not prepared or prepared.get('workspace_state') != 'prepared':
            if not in_place or (target / '.course').exists() or (target / '.course').is_symlink():
                raise ValueError('目的地已存在。新課程專案可用 --in-place 做無覆寫安裝；已有第二大腦或 .course 時先讀接入說明。')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='course-init-', dir=target.parent) as temp_name:
        source, info = fetch('ais-os', Path(temp_name), args.cache)
        for name in ('AGENTS.md', 'CLAUDE.md', 'aios-intake.md'):
            if not (source / name).is_file():
                raise ValueError('AIS-OS 必要檔案缺少：' + name)
        if (source / '.course').exists():
            raise ValueError('上游含保留進度目錄，停止以保護學員記錄。')
        if target.exists():
            conflicts = [child.name for child in source.iterdir()
                         if (target / child.name).exists() or (target / child.name).is_symlink()]
            if conflicts:
                raise ValueError('安裝前發現同名項目，未寫入任何 AIS-OS 檔案：' + ', '.join(sorted(conflicts)) + '。請比較既有內容，不刪除或覆寫。')
        progress = prepared or new_progress()
        progress.update(ais_os_commit=info['commit'], workspace_state='initialized')
        with (source / '.gitignore').open('a', encoding='utf-8') as f:
            f.write('\n# Student-local course state and credentials\n.course/\n.env\n.env.*\n!.env.example\n')
        if target.exists():
            for child in source.iterdir():
                child.rename(target / child.name)
        else:
            source.rename(target)
        write_json(target / '.course/progress.json', progress)
        write_json(target / '.course/installed.json', {})
        (target / '.course/README.md').write_text(
            '這是私人進度與筆記，不提交回課程 repo。請先讀 progress.json，再讀教材 START_HERE.md。\n', encoding='utf-8')
    return {'workspace': str(target), 'ais_os_skills': 6,
            'status': 'files_prepared', 'next': '在 AI 開啟這個工作區，驗收檔案與技能，再依進度進行背景訪談。'}


def install(args):
    ws = workspace(args.workspace)
    sources = json.loads(LOCK.read_text(encoding='utf-8'))['sources']
    info = sources[args.component]
    if not info.get('skills'):
        raise ValueError('這個來源不是可直接安裝的 Skill 包，請閱讀對應階段文件。')
    base = ws / AGENTS[args.agent]
    if ws not in base.resolve().parents:
        raise ValueError('技能目錄指向工作區外，停止安裝。')
    records = json.loads((ws / '.course/installed.json').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='course-install-') as temp_name:
        source, info = fetch(args.component, Path(temp_name), args.cache)
        candidates = []
        for skill in info['skills']:
            src = source / skill['path']
            if not (src / 'SKILL.md').is_file():
                raise ValueError('找不到技能：' + skill['name'])
            if args.component == 'agent-reach':
                # Keep the vendor tree unchanged; adapt only the student skill.
                prepared = Path(temp_name) / 'prepared-agent-reach'
                shutil.copytree(src, prepared)
                (prepared / 'SKILL.md').rename(prepared / 'SKILL.upstream.md')
                shutil.copyfile(ROOT / 'templates/agent-reach-skill.md', prepared / 'SKILL.md')
                shutil.copyfile(ROOT / 'docs/agent-reach.md', prepared / 'COURSE_SETUP.md')
                src = prepared
            dst = base / skill['name']
            if dst.is_symlink() or (dst.exists() and fingerprints(dst) != fingerprints(src)):
                raise ValueError('已存在不同版本，未修改任何技能：' + str(dst) + '。先保留客製內容，再由 AI 比較版本。')
            candidates.append((src, dst, skill))
        if args.component == 'marketing' and (source / 'tools').is_dir():
            src, dst = source / 'tools', base.parent / 'tools'
            if dst.is_symlink() or (dst.exists() and fingerprints(dst) != fingerprints(src)):
                raise ValueError('行銷共用 tools 已存在不同內容，未修改任何技能。')
            candidates.append((src, dst, {'name': 'marketing-shared-tools'}))
        base.mkdir(parents=True, exist_ok=True)
        for src, dst, skill in candidates:
            if not dst.exists():
                shutil.copytree(src, dst)
            records[str(dst.relative_to(ws))] = {'component': args.component, 'name': skill['name'],
                                                'commit': info['commit'], 'files': fingerprints(dst)}
        # Preserve shared tools, notices, and original repository layout separately.
        vendor = ws / '.course/sources' / (args.component + '-' + info['commit'][:12])
        if not vendor.exists():
            vendor.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, vendor)
        write_json(ws / '.course/installed.json', records)
    return {'status': 'files_installed', 'agent': args.agent,
            'skills': [s['name'] for s in info['skills']],
            'source_copy': str(vendor), 'next': '重新載入 AI 技能，讀回 SKILL.md 與附件，完成該階段的實作驗收。'}


def verify(args):
    ws = workspace(args.workspace)
    records = json.loads((ws / '.course/installed.json').read_text(encoding='utf-8'))
    results = []
    for path, record in records.items():
        actual = fingerprints(ws / path) if (ws / path).is_dir() else {}
        results.append({'skill': record['name'], 'path': path,
                        'intact': actual == record['files'], 'file_count': len(actual)})
    return {'status': 'integrity_check_only', 'checks': results,
            'all_intact': bool(results) and all(r['intact'] for r in results),
            'note': '檔案完整不代表 AI 已載入、帳號已授權或影片可輸出。'}


def progress(args):
    ws = workspace(args.workspace)
    path = ws / '.course/progress.json'
    data = load_progress(path)
    if args.command in ('mark', 'checkpoint'):
        record = data['steps'][args.step]
        if args.command == 'mark':
            if not args.evidence.strip():
                raise ValueError('進度必須附上可核對的檔案、測試結果或略過理由。')
            update = {'status': args.status, 'evidence': args.evidence}
        else:
            if not args.current_action.strip() or not args.next_action.strip():
                raise ValueError('斷點必須包含目前做到哪裡與下一個動作。')
            artifacts = []
            for value in args.artifact or []:
                artifact = (ws / value).resolve()
                if ws not in artifact.parents or not artifact.exists():
                    raise ValueError('斷點成果必須是私人工作區內已存在的檔案或資料夾。')
                artifacts.append(artifact.relative_to(ws).as_posix())
            update = {'status': 'blocked' if args.blocker else 'in_progress',
                      'current_action': args.current_action, 'next_action': args.next_action,
                      'next_question': args.question or '', 'blocker': args.blocker or '',
                      'artifacts': sorted(set(record.get('artifacts', []) + artifacts))}
        if re.search(r'(?:sk-|tvly-|ghp_|github_pat_)[A-Za-z0-9_-]{10,}', json.dumps(update)):
            raise ValueError('記錄疑似含金鑰。只記錄結果與檔名；這項檢查不能辨識所有秘密。')
        record.update(update, updated_at=datetime.now(timezone.utc).isoformat())
        write_json(path, data)
    todo = next((k for k in STEPS if data['steps'][k]['status'] not in ('passed', 'skipped')), None)
    core = [s['id'] for s in COURSE['stages'] if s['tier'] == 'core']
    return {'course_version': data['course_version'], 'next_step': todo,
            'resume': data['steps'].get(todo),
            'core_complete': all(data['steps'][k]['status'] == 'passed' for k in core),
            'not_passed': [k for k in core if data['steps'][k]['status'] != 'passed'],
            'steps': {k: data['steps'][k] for k in STEPS}}


def main(argv=None):
    parser = argparse.ArgumentParser(description='AI 超級個體課程：隔離安裝、完整性檢查與學習進度')
    subs = parser.add_subparsers(dest='command', required=True)
    subs.add_parser('doctor', help='只檢查工具是否存在，不安裝或讀取金鑰')
    for name in ('start', 'init', 'install', 'verify', 'status', 'mark', 'checkpoint'):
        p = subs.add_parser(name)
        p.add_argument('--workspace', required=True)
        if name in ('init', 'install'):
            p.add_argument('--cache', help='選填：已下載來源包的本機目錄，仍會核對 SHA-256')
        if name == 'init':
            p.add_argument('--in-place', action='store_true', help='在已建立的課程專案安裝；預先檢查所有同名衝突，不覆寫任何檔案')
        if name == 'install':
            p.add_argument('--component', choices=['content', 'human', 'marketing', 'agent-reach', 'interview', 'openchatcut', 'talking-video'], required=True)
            p.add_argument('--agent', choices=list(AGENTS), required=True)
        if name in ('mark', 'checkpoint'):
            p.add_argument('--step', choices=STEPS, required=True)
        if name == 'mark':
            p.add_argument('--status', choices=['passed', 'pending', 'blocked', 'skipped'], required=True)
            p.add_argument('--evidence', required=True)
        if name == 'checkpoint':
            p.add_argument('--current-action', required=True)
            p.add_argument('--next-action', required=True)
            p.add_argument('--question', help='下一題的題號或簡短題目；回答另存私人訪談檔')
            p.add_argument('--artifact', action='append', help='工作區內已存在的相對路徑，可重複指定')
            p.add_argument('--blocker')
    args = parser.parse_args(argv)
    try:
        if args.command == 'doctor':
            result = {'os': platform.system(), 'architecture': platform.machine(), 'python': platform.python_version(),
                      'tools': {x: bool(shutil.which(x)) for x in ('git', 'gh', 'node', 'npm', 'codex', 'claude', 'ffmpeg')},
                      'note': '桌面 App 不一定有 CLI；工具不存在不表示帳號不能用。外掛/API 授權未測。'}
        elif args.command == 'start':
            result = start(args)
        elif args.command == 'init':
            result = init(args)
        elif args.command == 'install':
            result = install(args)
        elif args.command == 'verify':
            result = verify(args)
        else:
            result = progress(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not (args.command == 'verify' and not result['all_intact']) else 2
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc), 'next': '停止這一階段，保留原檔並排除原因；不要標成已完成。'}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
