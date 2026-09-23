#!/usr/bin/env python3
"""Check deliverable structure, local Markdown links, and obvious secret leaks."""
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
errors = []
course = json.loads((ROOT / 'course-map.json').read_text(encoding='utf-8'))
ids = [s['id'] for s in course['stages']]
if len(set(ids)) != len(ids) or [s.get('order') for s in course['stages']] != list(range(1, len(ids) + 1)):
    errors.append('stage identity or ordering')
if course.get('schema') != 2:
    errors.append('course schema')
for stage in course['stages']:
    for field in ('student_inputs', 'actions', 'outputs', 'acceptance', 'classroom_source'):
        if not stage.get(field):
            errors.append('missing stage contract: ' + stage['id'] + '/' + field)
    if (ROOT / stage['guide']).is_file():
        guide = (ROOT / stage['guide']).read_text(encoding='utf-8')
        for heading in ('## 現在要做什麼', '## 需要學員提供', '## AI 帶領步驟', '## 留下什麼、做到什麼才算完成', '## 中途停下來'):
            if heading not in guide:
                errors.append('missing guide section: ' + stage['id'] + '/' + heading)
for stage in course['stages']:
    if not (ROOT / stage['guide']).is_file():
        errors.append('missing guide: ' + stage['guide'])
    if any(d not in ids or ids.index(d) >= ids.index(stage['id']) for d in stage['depends_on']):
        errors.append('invalid dependency: ' + stage['id'])
for path in ROOT.rglob('*.md'):
    if '.git' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
        link = urlsplit(href.strip('<>'))
        if link.scheme or link.netloc or not link.path:
            continue
        if not (path.parent / unquote(link.path)).exists():
            errors.append(str(path.relative_to(ROOT)) + ': broken link ' + href)
    for pattern in [r'/Users/' + r'[^/\s]+/', r'/Volumes/' + r'[^\s]+',
                    r'(?:tvly-|sk-|ghp_|github_pat_)[A-Za-z0-9_-]{18,}',
                    r'open_chat_id=|openChatId=|om_x100|ou_[0-9a-f]{20,}']:
        if re.search(pattern, text):
            errors.append(str(path.relative_to(ROOT)) + ': private data pattern')
lock = json.loads((ROOT / 'sources.lock.json').read_text(encoding='utf-8'))
for key, source in lock['sources'].items():
    if not re.fullmatch(r'[a-f0-9]{40}', source['commit']) or not re.fullmatch(r'[a-f0-9]{64}', source['archive_sha256']):
        errors.append('invalid source lock: ' + key)
    if source['archive_url'] != f"https://codeload.github.com/{source['repo']}/tar.gz/{source['commit']}":
        errors.append('unrecognized source host: ' + key)
for required in ['README.md', 'START_HERE.md', 'AGENTS.md', 'CLAUDE.md', 'LICENSE.md', 'VALIDATION.md',
                 'docs/course-sequence.md', 'templates/progress.md']:
    if not (ROOT / required).is_file():
        errors.append('missing: ' + required)
for removed in ('book', 'downloads'):
    if (ROOT / removed).exists():
        errors.append('book material must remain outside course repo: ' + removed)
print(json.dumps({'ok': not errors, 'stages': len(ids), 'sources': len(lock['sources']), 'errors': errors}, ensure_ascii=False, indent=2))
sys.exit(1 if errors else 0)
