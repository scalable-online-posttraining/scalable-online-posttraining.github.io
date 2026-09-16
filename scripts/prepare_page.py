"""One-time editorial conversion of the local archived HTML."""
from pathlib import Path
import html
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.tools/python'))
from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[1]
soup = BeautifulSoup((ROOT / 'original/index.html').read_text(), 'html.parser')
wrap = soup.select_one('.wrap')
headings = {
    'Foundation Models for General-Purpose Robots and the Performance Gap': ('Beyond pre-training', 'beyond-pretraining'),
    'Continual Learning in the Real World with Distributed Robot Fleets': ('Continual learning across a robot fleet', 'continual-learning'),
    'SOP: A Scalable Online Post-training Method': ('A scalable online post-training loop', 'method'),
    'SOP Performance and its Relation with Pre-training': ('Performance, fleet scale, and pre-training', 'results'),
    'Rapid Performance Gains in Novel Real-World Scenarios': ('Learning in new real-world environments', 'deployment'),
    'Towards Large-Scale Real-World Deployment': ('Towards large-scale real-world deployment', 'outlook'),
}
labels = {
    'EN_small': ('SOP: Scaling General-Purpose Robots in the Real World', ''),
    'GIF1_small': ('The SOP learning loop', ''),
    'GIF2_small': ('Learning through deployment', ''),
    '36h_laundary_folding': ('36 hours of continuous cloth folding', '50× speed · Full timelapse · 40:19'),
    '36h_box_assembly': ('36 hours of continuous box assembly', '50× speed · Full timelapse · 40:25'),
    'fold_cloth_4_no_audio': ('Cloth folding', 'Recovery example 1'),
    'box_assembly_1_no_audio': ('Box assembly', 'Recovery example'),
    'fold_cloth_1_no_audio': ('Cloth folding', 'Recovery example 2'),
    'fold_cloth_2_no_audio': ('Cloth folding', 'Recovery example 3'),
    'fold_cloth_3_no_audio': ('Cloth folding', 'Recovery example 4'),
    'top_display_cooler': ('Display cooler', 'Overhead view'),
    'front_display_cooler': ('Display cooler', 'Front view'),
    'closeup_freezer': ('Freezer', 'Close-up view'),
    'top_freezer': ('Freezer', 'Overhead view'),
    'top_shelf_restock_bottle': ('Bottle restocking', 'Overhead view'),
    'closeup_shelf_restock_bottle': ('Bottle restocking', 'Close-up view'),
    'front_restock': ('Shelf restocking', 'Front view'),
    'top_restock': ('Shelf restocking', 'Overhead view'),
    'front_fold_cloth_real': ('Cloth folding', 'Front view'),
    'top_box_assembly': ('Box assembly', 'Overhead view'),
    'top_fold_cloth_real': ('Cloth folding', 'Overhead view'),
    'closeup_fold_cloth_real': ('Cloth folding', 'Close-up view'),
}

def video_card(src, css='media'):
    old_name = Path(src).stem
    name = old_name.replace('36h_laundary_folding', '36h_laundry_folding')
    title, detail = labels[old_name]
    title = html.escape(title)
    long = '/timelapses/' in src
    accessible_title = title + (f', {html.escape(detail)}' if detail else '')
    attrs = f'controls playsinline preload="none" poster="assets/posters/{name}.jpg" aria-label="{accessible_title}"'
    if long:
        player = f'<video {attrs} data-hls="assets/hls/{name}/index.m3u8"></video><button class="hls-play" type="button" aria-label="Play {title}"><svg viewBox="0 0 16 16" aria-hidden="true"><path fill="currentColor" d="M3 1.5v13L14 8z"/></svg>Play timelapse</button>'
    else:
        player = f'<video {attrs}><source src="assets/videos/{name}.mp4" type="video/mp4">Your browser does not support HTML video.</video>'
    caption = title + (f'<span class="caption-meta">{detail}</span>' if detail else '')
    if old_name == 'EN_small':
        player = player.replace('preload="none"', 'preload="metadata"')
        caption = ''
    return f'<figure class="{css}"><div class="video-shell">{player}</div>' + (f'<figcaption>{caption}</figcaption>' if caption else '') + ('<p class="media-error" role="status" hidden></p>' if long else '') + '</figure>'

parts = []
copy = []
copy_id = ''
def flush():
    global copy, copy_id
    if copy:
        css = 'copy opening' if any('class="lede"' in s for s in copy) else 'copy'
        parts.append(f'<section class="{css}"'+(f' id="{copy_id}"' if copy_id else '')+'>'+''.join(copy)+'</section>')
        copy = []
        copy_id = ''

def gallery(sources, title, label):
    heading = f'<h3>{title}</h3>' if title else ''
    return f'<div class="gallery">{heading}<div class="video-row" tabindex="0" role="region" aria-label="{label}">' + ''.join(video_card(s, 'video-card') for s in sources) + '</div></div>'

children = [c for c in wrap.children if isinstance(c, Tag)]
started = False
long_sources = []
for node in children:
    if node.name == 'figure' and node.find('video') and 'EN_small' in node.video.get('src', ''):
        started = True
        parts.append(video_card(node.video['src'], 'media hero'))
        copy.append('<p class="lede">General-purpose robots are moving beyond static human demonstrations toward autonomous real-world learning. VLA models can keep improving after deployment, turning real-world experience into a scalable training resource.</p>')
        continue
    if not started or node.name == 'footer':
        continue
    if node.name == 'p':
        text = node.get_text(' ', strip=True)
        if text.startswith('For general-purpose robots to operate'):
            copy.append('<p>General-purpose robots need more than the ability to complete a task once. They must operate reliably in changing environments, generalize across tasks, and adapt as they encounter new situations in the physical world.</p>')
        elif text.startswith('We introduce'):
            copy.append('<p>We introduce <strong>SOP (Scalable Online Post-training)</strong>, a framework for updating Vision-Language-Action (VLA) models online across a robot fleet. Robots share experience through distributed online training, improving performance on complex tasks within hours.</p>')
        elif text.startswith('To validate the effectiveness'):
            copy.append('<p>We evaluate three questions: how SOP compares with offline post-training; how performance scales with the number of robots; and how online learning interacts with the scale of pre-training data.</p>')
        elif text.startswith('First, we needed to confirm'):
            copy.append('<p>We compare two representative algorithms, HG-DAgger and RECAP, both in their original settings and integrated into SOP. HG-DAgger originally used a single robot, while RECAP used offline training. Integrating either algorithm into SOP consistently improves performance across the evaluated tasks. For cloth folding and box assembly, recovery behaviors learned during online training also improve throughput.</p>')
        elif text.startswith('At the outset, we discussed'):
            copy.append('<p>We deployed the robot fleet in real-world environments unseen during pre-training. Changes in the surroundings initially reduced success rates and throughput, even on familiar tasks. After a few hours of online learning with SOP, the robots improved their performance across restocking, cloth folding, and box assembly.</p>')
        elif text.startswith('SOP changes more than just technical'):
            copy.append('<p>SOP makes deployment the starting point for continued learning. Instead of freezing a robot’s capabilities after training, experience from the fleet feeds back into a shared policy. Online updates, distributed exploration, and multi-task learning provide a path toward robots that improve as they operate in the real world.</p>')
        else:
            copy.append(str(node).replace('which is 12% higher', 'which is 12 percentage points higher'))
    elif node.name == 'h2':
        flush()
        heading, copy_id = headings[node.get_text(strip=True)]
        copy.append(f'<h2>{heading}</h2>')
    elif node.name == 'figure':
        if not node.find(['img', 'video']):
            continue
        flush()
        if node.find('video'):
            src = node.video['src']
            if '/timelapses/' in src:
                long_sources.append(src)
                if len(long_sources) == 2:
                    parts.append('<div class="long-grid">'+''.join(video_card(s, '') for s in long_sources)+'</div>')
            else:
                parts.append(video_card(src))
        else:
            node['class'] = 'media'
            node.img['decoding'] = 'async'
            from PIL import Image
            w, h = Image.open(ROOT / 'original' / node.img['src']).size
            node.img['width'], node.img['height'] = w, h
            parts.append(str(node))
    elif node.name == 'div' and 'grid' in node.get('class', []):
        flush()
        sources = [v['src'] for v in node.find_all('video')]
        if '/common/' in sources[0]:
            parts.append(gallery(sources[:8], 'Restocking in new environments', 'Restocking videos — scroll to explore all eight views'))
            parts.append(gallery(sources[8:], 'Cloth folding and box assembly', 'Cloth folding and box assembly videos — scroll to explore'))
        else:
            parts.append(gallery(sources, '', 'Recovery behaviors — scroll to explore all five examples'))
    elif node.name == 'table':
        flush()
        for th in node.find_all('th'): th['scope'] = 'col'
        node['aria-label'] = 'Fleet size, success rate after three hours, and time to reach 80 percent success'
        parts.append('<div class="table-wrap" tabindex="0" role="region" aria-label="Fleet scaling results">'+str(node)+'</div>')
flush()
title = 'SOP: Scaling General-Purpose Robots in the Real World'
document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="Scalable Online Post-training: continual learning across robot fleets, improving VLA policies through shared real-world experience.">
<link rel="canonical" href="https://scalable-online-posttraining.github.io/"><meta property="og:title" content="{title}"><meta property="og:description" content="Scalable Online Post-training for continual learning across robot fleets."><meta property="og:type" content="article"><meta property="og:url" content="https://scalable-online-posttraining.github.io/">
<meta name="theme-color" content="#f9f6f0"><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css">
<link rel="preload" href="assets/fonts/Satoshi-Medium.ttf" as="font" type="font/ttf" crossorigin><link rel="preload" href="assets/fonts/DMSans-Regular.ttf" as="font" type="font/ttf" crossorigin>
<script src="vendor/hls.min.js" defer></script><script src="player.js" defer></script></head>
<body id="top"><a class="skip-link" href="#article">Skip to research</a>
<header class="masthead"><div class="topline"><span class="project-label">SOP</span><time class="date" datetime="2026-01-06">January 6, 2026</time></div>
<h1>{title}</h1><div class="actions"><a class="paper-link" href="assets/sop.pdf" target="_blank" rel="noopener">Read Paper<svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M5 15 15 5M5 5h10v10" stroke="currentColor" stroke-width="1.5"/></svg></a></div></header>
<main id="article"><article>{''.join(parts)}</article></main>
<footer class="site-footer"><div><strong>SOP</strong><p>Scalable Online Post-training</p></div><a class="back-top" href="#top"><span>Back to top</span><span aria-hidden="true">↑</span></a></footer></body></html>'''
assert len(BeautifulSoup(document, 'html.parser').find_all('video')) == 22
assert 'agibot' not in document.lower()
(ROOT / 'public/index.html').write_text(BeautifulSoup(document, 'html.parser').prettify())
(ROOT / 'public/.nojekyll').touch()
print('Created SOP page with 22 videos and three research figures.')
