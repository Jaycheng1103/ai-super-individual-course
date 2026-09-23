#!/usr/bin/env python3
"""User-run local credential input and explicit, small API checks."""
import argparse
import getpass
import json
import mimetypes
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request
import uuid
from course import workspace, write_json


def request_json(request):
    try:
        with urllib.request.urlopen(request, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as exc:
        # Do not echo request headers, secret values, or a provider's raw body.
        raise ValueError(f'API 回傳 HTTP {exc.code}；請檢查權限、方案、額度及官方狀態。') from None
    except (urllib.error.URLError, TimeoutError):
        raise ValueError('API 網路連線失敗；尚未驗證成功。') from None


def configure(ws, service):
    if not sys.stdin.isatty():
        raise ValueError('請由學員本人在本機互動式終端執行；不接受聊天、命令參數或管線傳入金鑰。')
    folder = ws / '.course/secrets'
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    if ws not in folder.resolve().parents:
        raise ValueError('秘密設定目錄不能連到工作區外。')
    key = getpass.getpass('請貼上自己的 API key（輸入不會顯示）：').strip()
    if not key or any(c.isspace() for c in key):
        raise ValueError('金鑰空白或含空白字元，未儲存。')
    path = folder / (service + '.key')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(key)
    return {'status': 'saved_locally_not_tested', 'service': service}


def check(ws, service, allow_usage, audio=None, allow_upload=False):
    if not allow_usage:
        raise ValueError('先由學員確認這次可能耗用 API 額度，再加 --allow-usage。')
    key_file = ws / '.course/secrets' / (service + '.key')
    if key_file.is_symlink():
        raise ValueError('不讀取連結形式的金鑰檔。')
    key = key_file.read_text(encoding='utf-8').strip()
    if service == 'tavily':
        request = urllib.request.Request('https://api.tavily.com/search',
            data=json.dumps({'query': 'Tavily official documentation', 'max_results': 3, 'search_depth': 'basic'}).encode(),
            headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}, method='POST')
        result = request_json(request)
        urls = [r.get('url') for r in result.get('results', []) if r.get('url')]
        if not urls:
            raise ValueError('API 回應沒有可查來源，未通過搜尋驗收。')
        output = {'status': 'search_returned_sources', 'source_count': len(urls), 'sources': urls}
        write_json(ws / '.course/checks/tavily.json', output)
        return output
    if not audio or not allow_upload:
        raise ValueError('ElevenLabs 測試需指定本人可上傳的短音訊 --audio，並加 --allow-upload。')
    audio_path = Path(audio).expanduser().resolve()
    if audio_path.suffix.lower() not in ('.wav', '.mp3', '.m4a', '.ogg', '.flac', '.aac', '.mp4', '.webm'):
        raise ValueError('請使用一般音訊格式，例如 WAV、MP3 或 M4A。')
    if not audio_path.is_file() or audio_path.stat().st_size > 10 * 1024 * 1024:
        raise ValueError('只接受存在且小於 10 MB 的測試音訊。請先準備約 10–20 秒片段。')
    boundary = 'course-' + uuid.uuid4().hex
    mime = mimetypes.guess_type(audio_path.name)[0] or 'application/octet-stream'
    # Use a generic filename; don't send a student's directory or original filename.
    data = (f'--{boundary}\r\nContent-Disposition: form-data; name="model_id"\r\n\r\nscribe_v2\r\n'
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="sample{audio_path.suffix}"\r\n'
            f'Content-Type: {mime}\r\n\r\n').encode() + audio_path.read_bytes() + f'\r\n--{boundary}--\r\n'.encode()
    request = urllib.request.Request('https://api.elevenlabs.io/v1/speech-to-text', data=data,
        headers={'xi-api-key': key, 'Content-Type': 'multipart/form-data; boundary=' + boundary}, method='POST')
    result = request_json(request)
    if not result.get('text', '').strip():
        raise ValueError('沒有回傳可讀逐字稿，尚未通過驗收。')
    dest = ws / '.course/checks/elevenlabs-transcript.json'
    write_json(dest, result)
    return {'status': 'transcript_received_needs_listening_review', 'output': str(dest),
            'characters': len(result['text']), 'next': '學員回聽原音核對文字；此結果不代表 OpenChatCut 已連線。'}


def main():
    p = argparse.ArgumentParser(description='學員自己的 Tavily／ElevenLabs 設定與小型測試')
    p.add_argument('action', choices=['configure', 'check'])
    p.add_argument('--workspace', required=True)
    p.add_argument('--service', choices=['tavily', 'elevenlabs'], required=True)
    p.add_argument('--allow-usage', action='store_true')
    p.add_argument('--allow-upload', action='store_true')
    p.add_argument('--audio')
    a = p.parse_args()
    try:
        ws = workspace(a.workspace)
        result = configure(ws, a.service) if a.action == 'configure' else check(ws, a.service, a.allow_usage, a.audio, a.allow_upload)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except FileExistsError:
        print('設定已存在，未覆寫。換金鑰請由本人在本機編輯，勿貼到聊天。', file=sys.stderr)
    except FileNotFoundError:
        print('找不到工作區、金鑰或素材；請先完成設定。', file=sys.stderr)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
