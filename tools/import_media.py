"""Import selected media from a folder or ZIP into IITaku's static portfolio."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import warnings
import zipfile
from content_common import atomic_bytes, checked_path, commit_files, ensure_content_dependencies, project_root

IMAGES = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff'}
VIDEOS = {'.mp4', '.mov', '.m4v', '.webm'}
PRIVATE_PARTS = {'messages', 'inbox', 'contacts', 'connections', 'ads_information', 'accounts_center', '__macosx'}
ROLES = {'main', 'portrait', 'product', 'avatar'}
MANIFEST = 'frontend/public/media/portfolio.json'
PAGES_PUBLIC_LIMIT = 920 * 1024**2

def default_cache_dir() -> Path:
    if os.environ.get('IITAKU_MEDIA_CACHE_DIR'): return Path(os.environ['IITAKU_MEDIA_CACHE_DIR'])
    base = Path(os.environ.get('LOCALAPPDATA', os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))))
    return base / 'IITaku' / 'media-cache-v2'

def cache_matches(folder: Path, names: list[str], recipe: str) -> bool:
    try:
        record = json.loads((folder / 'complete.json').read_text(encoding='utf-8'))
        return record.get('recipe') == recipe and all((folder / name).is_file()
            and record.get('files', {}).get(name) == sha256(folder / name) for name in names)
    except (OSError, ValueError): return False

def mark_cache(folder: Path, names: list[str], recipe: str) -> None:
    atomic_bytes(folder / 'complete.json', json_bytes({'recipe': recipe,
        'files': {name: sha256(folder / name) for name in names}}))
    for frame in folder.glob('frame-*.png'): frame.unlink(missing_ok=True)

def validate_public_size(root: Path, updates: dict[str, bytes | Path]) -> int:
    prefix = 'frontend/public/'
    sizes = {path.relative_to(root).as_posix(): path.stat().st_size
        for path in (root / 'frontend/public').rglob('*') if path.is_file()}
    for relative, source in updates.items():
        if relative.startswith(prefix): sizes[relative] = len(source) if isinstance(source, bytes) else source.stat().st_size
    total = sum(sizes.values())
    print(f'Published public assets after update: {total / 1024**2:.1f} MiB', flush=True)
    if total > PAGES_PUBLIC_LIMIT:
        raise ValueError(f'Public assets would total {total / 1024**2:.1f} MiB, above this updater\'s 920 MiB budget for GitHub Pages. '
            'Select fewer videos or host the videos separately. Completed conversions are cached; no website files changed.')
    return total

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''): digest.update(block)
    return digest.hexdigest()

def selected(name: str, images_only: bool = False) -> bool:
    parts = Path(name.replace('\\', '/')).parts
    return bool(parts) and not any(part.lower() in PRIVATE_PARTS or part.startswith('.') for part in parts) \
        and Path(name).suffix.lower() in (IMAGES if images_only else IMAGES | VIDEOS)

@contextmanager
def source_files(source: Path, images_only: bool = False):
    if source.is_dir():
        yield [(path.relative_to(source).as_posix(), path) for path in sorted(source.rglob('*'))
               if path.is_file() and not path.is_symlink() and selected(path.relative_to(source).as_posix(), images_only)]
    elif source.is_file() and zipfile.is_zipfile(source):
        with tempfile.TemporaryDirectory(prefix='iitaku-source-') as name:
            folder = Path(name); files = []
            with zipfile.ZipFile(source) as archive:
                entries = [entry for entry in archive.infolist() if not entry.is_dir() and selected(entry.filename, images_only)]
                if len(entries) > 1000: raise ValueError('The archive has more than 1000 media files. Import smaller selections.')
                if sum(entry.file_size for entry in entries) > 4 * 1024**3: raise ValueError('Selected media exceeds 4 GiB. Split the archive.')
                for index, entry in enumerate(entries):
                    if entry.file_size > 256 * 1024**2:
                        raise ValueError(f'{entry.filename}: larger than 256 MiB. Import a smaller web copy.')
                    # Never extract archive paths. Each source gets a generated local filename.
                    target = folder / f'{index}{Path(entry.filename).suffix.lower()}'
                    with archive.open(entry) as incoming, target.open('wb') as outgoing:
                        shutil.copyfileobj(incoming, outgoing)
                    files.append((entry.filename.replace('\\', '/'), target))
            yield files
    elif source.is_file() and source.suffix.lower() in IMAGES | VIDEOS:
        yield [(source.name, source)] if not images_only or source.suffix.lower() in IMAGES else []
    else: raise ValueError('Provide an existing media folder, ZIP, image, or video.')

def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

def load_manifest(root: Path) -> dict:
    path = root / MANIFEST
    if not path.exists(): return {'version': 1, 'hero': {}, 'items': []}
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('version') != 1 or not isinstance(data.get('items'), list) or not isinstance(data.get('hero', {}), dict):
        raise ValueError('Existing portfolio.json is invalid. Repair it before importing.')
    return data

def validate_manifest_assets(root: Path, manifest: dict) -> None:
    if manifest.get('version') != 1 or not isinstance(manifest.get('items'), list):
        raise ValueError('Invalid existing portfolio manifest.')
    for item in manifest['items']:
        if not isinstance(item, dict): raise ValueError('Invalid existing gallery item.')
        for key in ['src', 'thumbnail'] + (['poster'] if item.get('poster') else []):
            value = item.get(key)
            if not isinstance(value, str) or not value.startswith(('media/', 'art/')):
                raise ValueError('Existing gallery asset must be a local media/ or art/ path.')
            checked_path(root, 'frontend/public/' + value)

def prepare_import(root: Path, source: Path, staging: Path, *, metadata: Path | None = None,
                   replace: bool = False, images_only: bool = False, base_manifest: dict | None = None,
                   bundled_public: Path | None = None, max_total_mb: float = 900,
                   cache_dir: Path | None = None) -> dict[str, bytes | Path]:
    from PIL import Image, ImageCms, ImageOps, ImageStat
    Image.MAX_IMAGE_PIXELS = 40_000_000
    warnings.simplefilter('error', Image.DecompressionBombWarning)
    if not 0 < max_total_mb <= 900: raise ValueError('--max-total-mb must be greater than 0 and at most 900.')
    cache_dir = (cache_dir or default_cache_dir()).expanduser().resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)
    config_path = metadata or root / 'tools/content-map.json'
    config = json.loads(config_path.read_text(encoding='utf-8')) if config_path.exists() else {}
    mappings = config.get('files', {})
    if not isinstance(mappings, dict): raise ValueError('content-map.json files must be an object.')
    manifest = base_manifest if base_manifest is not None else load_manifest(root)
    validate_manifest_assets(root, manifest)
    original = manifest['items']
    existing = {item.get('contentHash'): item for item in original if item.get('contentHash')}
    items = [] if replace else list(original)
    hero = dict(manifest.get('hero', {}))
    updates: dict[str, bytes | Path] = {}
    failures, skipped, seen, successful = [], 0, set(), 0
    ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')

    def save_image(image, destination: Path, edge: int, quality: int):
        result = image.copy()
        result.thumbnail((edge, edge), Image.Resampling.LANCZOS)
        result.save(destination, 'WEBP', quality=quality, method=6)
        return result.size

    with source_files(source, images_only) as files:
        if len(files) > 1000: raise ValueError('Import at most 1000 media files at a time.')
        for index, (relative, path) in enumerate(files, 1):
            meta = mappings.get(relative, mappings.get(Path(relative).name, {}))
            if not isinstance(meta, dict): raise ValueError(f'Invalid metadata for {relative}')
            if meta.get('hero') and meta['hero'] not in ROLES: raise ValueError(f'{relative}: invalid hero role')
            if meta.get('replaceArt') and meta['replaceArt'] not in {
                'tunnel', 'portrait-drawing', 'product', 'energy', 'illustration', 'environment',
                'clock', 'chair', 'cube', 'iitaku-avatar', 'toon-shader', 'neon-shader'}:
                raise ValueError(f'{relative}: invalid artwork replacement slot')
            if meta.get('include') is False or (images_only and path.suffix.lower() in VIDEOS):
                skipped += 1; continue
            print(f'[{index}/{len(files)}] {Path(relative).name}', flush=True)
            digest = sha256(path)
            if digest in seen: skipped += 1; continue
            seen.add(digest)
            old = existing.get(digest)
            identifier = 'work-' + digest[:20]
            kind = 'video' if path.suffix.lower() in VIDEOS else 'image'
            recipe = hashlib.sha256(json_bytes({'version': 2, 'source': digest,
                'posterSeconds': meta.get('posterSeconds'), 'videoEdge': 1280, 'crf': 21,
                'imageEdge': 1920, 'imageQuality': 94})).hexdigest()
            folder = cache_dir / recipe; folder.mkdir(parents=True, exist_ok=True)
            names = ['video.mp4', 'thumb.webp', 'poster.webp'] if kind == 'video' else ['image.webp', 'thumb.webp']
            src = f'media/{identifier}.mp4' if kind == 'video' else f'media/{identifier}.webp'
            thumbnail = f'media/{identifier}-thumb.webp'
            # Reuse optimized content and titles on repeated imports.
            public = root / 'frontend/public'
            keys = ['src', 'thumbnail'] + (['poster'] if kind == 'video' else [])
            reusable = old and all((public / old.get(key, 'missing')).is_file() for key in keys)
            if not reusable and old and bundled_public and all((bundled_public / old.get(key, 'missing')).is_file() for key in keys):
                public, reusable = bundled_public, True
            try:
                if reusable:
                    src, thumbnail = old['src'], old['thumbnail']
                    poster = public / thumbnail
                    poster_full = public / (old.get('poster') or old['src'])
                elif cache_matches(folder, names, recipe):
                    print('  Reusing cached conversion.', flush=True)
                    poster = folder / 'thumb.webp'
                    poster_full = folder / ('poster.webp' if kind == 'video' else 'image.webp')
                    updates['frontend/public/' + src] = folder / ('video.mp4' if kind == 'video' else 'image.webp')
                    updates['frontend/public/' + thumbnail] = poster
                    if kind == 'video': updates[f'frontend/public/media/{identifier}-poster.webp'] = poster_full
                elif kind == 'image':
                    with Image.open(path) as decoded:
                        image = ImageOps.exif_transpose(decoded)
                        profile = image.info.get('icc_profile')
                        mode = 'RGBA' if 'A' in image.getbands() or image.info.get('transparency') is not None else 'RGB'
                        if profile:
                            try:
                                image = ImageCms.profileToProfile(image, ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                                    ImageCms.createProfile('sRGB'), outputMode=mode)
                            except (ValueError, OSError, ImageCms.PyCMSError): image = image.convert(mode)
                        else: image = image.convert(mode)
                        full, poster = folder / 'image.webp', folder / 'thumb.webp'
                        save_image(image, full, 1920, 94); save_image(image, poster, 800, 88)
                    updates['frontend/public/' + src] = full
                    updates['frontend/public/' + thumbnail] = poster
                    poster_full = full
                else:
                    if not ffmpeg or not ffprobe:
                        raise ValueError('FFmpeg and FFprobe are required for videos; install FFmpeg or use --images-only.')
                    info = json.loads(subprocess.check_output([ffprobe, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))
                    video = next(stream for stream in info['streams'] if stream['codec_type'] == 'video')
                    duration = float(info['format'].get('duration', video.get('duration', 0)))
                    if not 0 < duration <= 600: raise ValueError('Use a video between 0 and 600 seconds for the portfolio.')
                    output = folder / 'video.mp4'
                    command = [ffmpeg, '-v', 'error', '-nostdin', '-y', '-i', str(path), '-map', '0:v:0', '-map', '0:a?',
                        '-vf', "scale=w='min(1280,iw)':h='min(1280,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2",
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', '-map_metadata', '-1', str(output)]
                    subprocess.run(command, check=True)
                    if output.stat().st_size > 95 * 1024**2: raise ValueError('Web video exceeds 95 MiB. Use a shorter clip.')
                    # Choose a detailed frame, rather than an intro card or a black fade.
                    times = [max(0, min(duration - 0.05, float(meta['posterSeconds'])))] if 'posterSeconds' in meta \
                        else [duration * fraction for fraction in (0.05, 0.15, 0.25, 0.4, 0.6, 0.75)]
                    best, score = None, -1.0
                    for sample, seconds in enumerate(times):
                        frame = folder / f'frame-{sample}.png'
                        subprocess.run([ffmpeg, '-v', 'error', '-nostdin', '-y', '-ss', str(seconds), '-i', str(output),
                            '-frames:v', '1', str(frame)], check=True)
                        with Image.open(frame) as decoded:
                            image = decoded.convert('RGB'); gray = image.convert('L'); gray.thumbnail((160, 160))
                            value = gray.entropy() * min(1.0, ImageStat.Stat(gray).mean[0] / 25)
                            if value > score: score, best = value, image.copy()
                    if best is None: raise ValueError('Could not generate a video poster.')
                    poster, poster_full = folder / 'thumb.webp', folder / 'poster.webp'
                    save_image(best, poster, 800, 90); save_image(best, poster_full, 1920, 94)
                    updates['frontend/public/' + src] = output
                    updates['frontend/public/' + thumbnail] = poster
                    updates[f'frontend/public/media/{identifier}-poster.webp'] = poster_full
                if not reusable and not cache_matches(folder, names, recipe): mark_cache(folder, names, recipe)
                item = dict(old or {})
                item.update({'id': identifier, 'kind': kind, 'src': src, 'thumbnail': thumbnail,
                    'contentHash': digest, 'sourceFile': Path(relative).name,
                    'title': meta.get('title', item.get('title', f'Portfolio {"film" if kind == "video" else "artwork"} {index:02d}')),
                    'category': meta.get('category', item.get('category', 'Films' if kind == 'video' else 'Portfolio')),
                    'caption': meta.get('caption', item.get('caption', '')),
                    'alt': meta.get('alt', item.get('alt', meta.get('title', 'Selected portfolio work')))})
                if not all(isinstance(item[key], str) for key in ['title', 'category', 'caption', 'alt']):
                    raise ValueError('Title, category, caption, and alt must be strings.')
                if kind == 'video': item['poster'] = f'media/{identifier}-poster.webp'
                items = [entry for entry in items if entry.get('contentHash') != digest and entry.get('id') != identifier]
                items.append(item)
                if meta.get('hero'):
                    role = meta['hero']
                    if role not in ROLES: raise ValueError('hero must be main, portrait, product, or avatar.')
                    if kind == 'image': hero[role] = {'src': src, 'alt': item['alt']}
                    else: hero[role] = {'src': item['poster'], 'alt': item['alt']}
                if meta.get('replaceArt'):
                    replacement = meta['replaceArt']
                    allowed = {'tunnel', 'portrait-drawing', 'product', 'energy', 'illustration', 'environment', 'clock', 'chair', 'cube', 'iitaku-avatar', 'toon-shader', 'neon-shader'}
                    if replacement not in allowed: raise ValueError('replaceArt must name an existing artwork slot.')
                    updates[f'frontend/public/art/{replacement}.webp'] = poster_full
                successful += 1
            except (OSError, ValueError, StopIteration, subprocess.SubprocessError,
                    Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
                # Drop this item's staged writes and preserve existing published content.
                for key in list(updates):
                    if identifier in key: del updates[key]
                failures.append({'file': relative, 'reason': str(error)[:250]})
                print(f'  Skipped: {error}', file=sys.stderr)
    if not successful: raise ValueError('No usable media was selected. Existing gallery is unchanged.')
    if failures:
        raise ValueError(f'{len(failures)} files could not be imported; no content changed. Fix the reported files or exclude them in content-map.json.')
    size = sum(len(value) if isinstance(value, bytes) else value.stat().st_size for value in updates.values())
    print(f'Prepared new/updated web media: {size / 1024**2:.1f} MiB (budget {max_total_mb:g} MiB).', flush=True)
    if size > max_total_mb * 1024**2:
        raise ValueError(f'New web media totals {size / 1024**2:.1f} MiB, above the {max_total_mb:g} MiB budget. '
            'Use a higher --max-total-mb value up to 900, or select fewer videos. Completed conversions are cached; no website files changed.')
    manifest = {'version': 1, 'hero': hero, 'items': items}
    updates[MANIFEST] = json_bytes(manifest)
    validate_public_size(root, updates)
    report = {'filesSkipped': skipped, 'failures': failures, 'galleryItems': len(items)}
    (staging / 'import-report.json').write_bytes(json_bytes(report))
    print(f'Prepared {len(items)} gallery items; {skipped} duplicates/exclusions; {len(failures)} errors.')
    return updates

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Media ZIP, folder, image, or video')
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--metadata', type=Path, help='JSON titles, categories, exclusions, and hero roles')
    parser.add_argument('--replace-gallery', action='store_true', help='Replace the gallery instead of appending')
    parser.add_argument('--images-only', action='store_true', help='Skip videos; FFmpeg is not required')
    parser.add_argument('--max-total-mb', type=float, default=900, help='New media budget in MiB (default 900; maximum 900)')
    parser.add_argument('--cache-dir', type=Path, help='Optional conversion cache folder outside the repository')
    args = parser.parse_args()
    try:
        root = project_root(args.project)
        if sys.version_info < (3, 10): raise ValueError('Python 3.10 or later is required.')
        ensure_content_dependencies()
        with tempfile.TemporaryDirectory(prefix='iitaku-import-') as name:
            updates = prepare_import(root, args.source.resolve(), Path(name), metadata=args.metadata,
                replace=args.replace_gallery, images_only=args.images_only,
                max_total_mb=args.max_total_mb, cache_dir=args.cache_dir)
            commit_files(root, updates, 'content')
    except ImportError:
        print('Pillow is required. Run: py -m pip install Pillow==12.3.0', file=sys.stderr); return 1
    except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError, subprocess.SubprocessError) as error:
        print(f'Import stopped: {error}', file=sys.stderr); return 1
    return 0

if __name__ == '__main__': sys.exit(main())
