"""Deployment gate: complete references, lazy media, HLS duration, and size limits."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re

ROOT = Path(__file__).resolve().parents[1] / 'public'

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.videos = []
        self.figures = []
        self.ids = []
        self.anchors = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs: self.ids.append(attrs['id'])
        if tag == 'video': self.videos.append(attrs)
        if tag == 'img': self.figures.append(attrs)
        for key in ['src', 'href', 'poster', 'data-hls']:
            if key not in attrs: continue
            ref = attrs[key]
            if ref.startswith('#'): self.anchors.append(ref[1:])
            elif not urlsplit(ref).scheme: self.refs.append(ref)

def check():
    source = (ROOT / 'index.html').read_text()
    page = Page(); page.feed(source)
    assert 'agibot' not in source.lower(), 'Unexpected page branding'
    assert len(page.videos) == 22, 'Video missing'
    assert len({v.get('aria-label') for v in page.videos}) == 22, 'Video labels must distinguish each example'
    assert len(page.figures) == 3, 'Research figure missing'
    assert len(set(page.ids)) == len(page.ids), 'Duplicate anchor IDs'
    assert set(page.anchors) <= set(page.ids), 'Broken anchor'
    assert sum('data-hls' in v for v in page.videos) == 2
    for v in page.videos:
        assert all(k in v for k in ['controls', 'playsinline', 'poster', 'aria-label'])
        assert v['preload'] in ['none', 'metadata']
        assert 'autoplay' not in v
    page.refs += re.findall(r'url\([\'"]?([^\)\'\"]+)', (ROOT / 'style.css').read_text())
    for ref in page.refs:
        assert not ref.startswith('/'), f'Root-relative URL breaks project Pages: {ref}'
        file = (ROOT / unquote(urlsplit(ref).path)).resolve()
        assert file.is_relative_to(ROOT.resolve()), f'Outside publication: {ref}'
        assert file.is_file(), f'Missing asset: {ref}'
    media = json.loads((ROOT / 'media.json').read_text())
    assert len(media) == 22
    expected_sources = {m['src'] for m in media}
    assert expected_sources <= set(page.refs), 'Manifest video omitted from page'
    segments = 0
    for m in media:
        if m['kind'] != 'hls': continue
        playlist = ROOT / m['src']
        body = playlist.read_text()
        assert '#EXT-X-ENDLIST' in body, 'Incomplete long video'
        assert '#EXT-X-PLAYLIST-TYPE:VOD' in body
        duration = sum(float(x) for x in re.findall(r'#EXTINF:([\d.]+)', body))
        assert abs(duration - m['duration']) < 1, (playlist, duration, m['duration'])
        for line in body.splitlines():
            if line and not line.startswith('#'):
                segment = playlist.parent / line
                assert segment.is_file() and segment.stat().st_size > 0, f'Missing HLS segment: {segment}'
                segments += 1
    files = [p for p in ROOT.rglob('*') if p.is_file()]
    assert all(f.stat().st_size < 90 * 2**20 for f in files), 'File exceeds 90 MiB'
    total = sum(f.stat().st_size for f in files)
    assert total < 800 * 2**20, f'Publication is too large: {total / 2**20:.1f} MiB'
    assert not any('agibot' in str(f.relative_to(ROOT)).lower() for f in files)
    print(f'PASS: 22 videos, 3 research figures, {segments} HLS segments, {len(page.refs)} asset references; {total / 2**20:.1f} MiB.')

if __name__ == '__main__': check()
