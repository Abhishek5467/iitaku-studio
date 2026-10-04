"""Atomic content writes and reversible backups. Python standard library only."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import tempfile
import subprocess
import sys
import venv
from datetime import datetime
from uuid import uuid4

def ensure_content_dependencies() -> None:
    """Re-run the current command in a cached environment when Pillow is missing."""
    try:
        import PIL
        if PIL.__version__ == '12.3.0': return
    except ImportError: pass
    cache = Path(os.environ.get('LOCALAPPDATA', os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))))
    environment = cache / 'IITaku' / f'content-python-{sys.version_info.major}{sys.version_info.minor}'
    python = environment / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if not python.exists():
        print('Creating an isolated content-tools environment (one-time setup).', flush=True)
        venv.EnvBuilder(with_pip=True).create(environment)
    check = subprocess.run([str(python), '-c', "import PIL; assert PIL.__version__ == '12.3.0'"], capture_output=True)
    if check.returncode:
        subprocess.run([str(python), '-m', 'pip', 'install', 'Pillow==12.3.0'], check=True)
    raise SystemExit(subprocess.call([str(python), str(Path(sys.argv[0]).resolve()), *sys.argv[1:]]))

def project_root(value: str | Path) -> Path:
    root = Path(value).expanduser().resolve()
    if root.name == 'frontend' and (root / 'package.json').is_file():
        root = root.parent
    if not (root / 'frontend/package.json').is_file() or not (root / 'frontend/components/portfolio.tsx').is_file():
        raise ValueError('Choose the repository root containing the frontend folder.')
    return root

def checked_path(root: Path, relative: str) -> Path:
    parts = Path(relative).parts
    if Path(relative).is_absolute() or '..' in parts or '\\' in relative or not parts:
        raise ValueError(f'Unsafe relative path: {relative}')
    destination = root.joinpath(*parts)
    cursor = destination
    while cursor != root:
        if cursor.is_symlink():
            raise ValueError(f'Will not write through a symlink: {relative}')
        cursor = cursor.parent
    if destination.exists() and not destination.is_file():
        raise ValueError(f'Expected a file: {relative}')
    return destination

def atomic_bytes(destination: Path, data: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix='.iitaku-', dir=destination.parent)
    try:
        with os.fdopen(handle, 'wb') as stream:
            stream.write(data)
        os.replace(name, destination)
    finally:
        if os.path.exists(name): os.unlink(name)

def atomic_source(destination: Path, source: bytes | Path) -> None:
    if isinstance(source, bytes):
        atomic_bytes(destination, source)
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix='.iitaku-', dir=destination.parent)
    try:
        with os.fdopen(handle, 'wb') as outgoing, source.open('rb') as incoming:
            shutil.copyfileobj(incoming, outgoing, length=1024 * 1024)
        os.replace(name, destination)
    finally:
        if os.path.exists(name): os.unlink(name)

def same_source(destination: Path, source: bytes | Path) -> bool:
    if not destination.exists(): return False
    if isinstance(source, bytes):
        return destination.stat().st_size == len(source) and destination.read_bytes() == source
    if destination.stat().st_size != source.stat().st_size: return False
    with destination.open('rb') as current, source.open('rb') as incoming:
        while True:
            left, right = current.read(1024 * 1024), incoming.read(1024 * 1024)
            if left != right: return False
            if not left: return True

def commit_files(root: Path, updates: dict[str, bytes | Path], label: str) -> Path | None:
    changes = {}
    for relative, source in updates.items():
        destination = checked_path(root, relative)
        if not same_source(destination, source): changes[relative] = source
    if not changes:
        print('Already up to date. No files changed.')
        return None
    backup = root.parent / f'{root.name}-{label}-backup-{datetime.now():%Y%m%d-%H%M%S}-{uuid4().hex[:6]}'
    backup.mkdir()
    entries = []
    for relative in changes:
        destination = checked_path(root, relative)
        exists = destination.exists()
        entries.append({'path': relative, 'existed': exists})
        if exists:
            saved = backup / 'files' / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, saved)
    (backup / 'backup.json').write_text(json.dumps({'project': str(root), 'files': entries}, indent=2), encoding='utf-8')
    written = []
    try:
        for relative, data in changes.items():
            atomic_source(checked_path(root, relative), data)
            written.append(relative)
    except BaseException:
        for relative in reversed(written):
            entry = next(item for item in entries if item['path'] == relative)
            destination = checked_path(root, relative)
            if entry['existed']: atomic_source(destination, backup / 'files' / relative)
            else: destination.unlink(missing_ok=True)
        raise
    print(f'Applied {len(changes)} files. Backup: {backup}')
    return backup

def restore_backup(backup: Path, root: Path) -> None:
    record = json.loads((backup / 'backup.json').read_text(encoding='utf-8'))
    updates = {}
    deletes = []
    for entry in record['files']:
        relative = entry['path']; checked_path(root, relative)
        if entry['existed']: updates[relative] = backup / 'files' / relative
        else: deletes.append(checked_path(root, relative))
    # Preserve today's files before restoring the old copies.
    current = {entry['path']: checked_path(root, entry['path'])
               for entry in record['files'] if checked_path(root, entry['path']).exists()}
    undo = root.parent / f'{root.name}-before-restore-{uuid4().hex[:8]}'
    undo.mkdir()
    for relative, data in current.items(): atomic_source(undo / relative, data)
    for relative, data in updates.items(): atomic_source(checked_path(root, relative), data)
    for destination in deletes: destination.unlink(missing_ok=True)
    print(f'Restored backup. Current copies preserved in: {undo}')
