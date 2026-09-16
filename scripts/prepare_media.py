"""Create complete, size-bounded web media from the local original archive."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FFMPEG = next((ROOT / '.tools/python/imageio_ffmpeg/binaries').glob('ffmpeg-*'))
PUBLIC = ROOT / 'public'

def run(args):
    p = subprocess.run([str(FFMPEG), '-hide_banner', '-loglevel', 'error', '-y', *args], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr)

def prepare(source):
    name = source.stem.replace('36h_laundary_folding', '36h_laundry_folding')
    probe = subprocess.run([str(FFMPEG), '-hide_banner', '-i', str(source)], capture_output=True, text=True).stderr
    match = re.search(r'Duration: (\d+):(\d+):([\d.]+)', probe)
    duration = int(match[1]) * 3600 + int(match[2]) * 60 + float(match[3])
    poster = PUBLIC / 'assets/posters' / f'{name}.jpg'
    run(['-ss', str(min(5, duration / 3)), '-i', str(source), '-frames:v', '1', '-vf', 'scale=960:-2', '-q:v', '3', str(poster)])
    is_long = source.parent.name == 'timelapses'
    common = ['-i', str(source), '-map', '0:v:0', '-map', '0:a?', '-vf', 'scale=w=min(iw\\,1920):h=min(ih\\,1080):force_original_aspect_ratio=decrease:force_divisible_by=2', '-c:v', 'h264_videotoolbox', '-pix_fmt', 'yuv420p', '-b:v', '1200k', '-c:a', 'aac', '-b:a', '96k', '-map_metadata', '-1']
    if is_long:
        output = PUBLIC / 'assets/hls' / name / 'index.m3u8'
        output.parent.mkdir(parents=True, exist_ok=True)
        common[common.index('-vf') + 1] = 'scale=1280:720'
        common[common.index('-b:v') + 1] = '650k'
        common[common.index('-b:a') + 1] = '64k'
        run([*common, '-force_key_frames', 'expr:gte(t,n_forced*6)', '-hls_time', '6', '-hls_playlist_type', 'vod', '-hls_flags', 'independent_segments', '-hls_segment_filename', str(output.parent / 'part-%04d.ts'), str(output)])
    else:
        output = PUBLIC / 'assets/videos' / f'{name}.mp4'
        run([*common, '-movflags', '+faststart', str(output)])
    result = {'original': str(source.relative_to(ROOT / 'original')), 'src': str(output.relative_to(PUBLIC)), 'poster': str(poster.relative_to(PUBLIC)), 'duration': duration, 'kind': 'hls' if is_long else 'mp4'}
    print(f'Prepared {name}: {duration:.1f}s ({result["kind"]})', flush=True)
    return result

if __name__ == '__main__':
    for name in ['main_res.png', 'sop_framwork.png', 'abl_pretrain_data_scale.png']:
        shutil.copy2(ROOT / 'original/assets/images' / name, PUBLIC / 'assets/images' / name)
    shutil.copy2(ROOT / 'original/assets/sop.pdf', PUBLIC / 'assets/sop.pdf')
    for font in (ROOT.parent / 'lwd-blog-source/public/fonts').glob('*.ttf'):
        shutil.copy2(font, PUBLIC / 'assets/fonts' / font.name)
    with ThreadPoolExecutor(max_workers=3) as pool:
        media = list(pool.map(prepare, sorted((ROOT / 'original/assets/videos').rglob('*.mp4'))))
    (PUBLIC / 'media.json').write_text(json.dumps(media, indent=2) + '\n')
    print(f'Done: {len(media)} videos; {sum(f.stat().st_size for f in PUBLIC.rglob("*") if f.is_file()) / 2**20:.1f} MiB', flush=True)
