# SOP research website

Website: https://scalable-online-posttraining.github.io/

The `public/` directory is a self-contained static website. Its typography and layout follow the LWD, τ0-WM, and τ0-VLA research pages. It includes the original paper, three research figures, and 22 full-length videos. Two long timelapses use local HLS segments. No external font or video service is required.

## Hosting

The repository is `scalable-online-posttraining/scalable-online-posttraining.github.io`, in the GitHub organization managed by `tauteamhq`. GitHub Pages publishes the site at the organization domain root using GitHub Actions. The repository was transferred with all media and commit history preserved; the previous publication at `tauteamhq.github.io/sop/` was withdrawn.

## Validation and deployment

Run `python3 scripts/check_site.py` before publishing. Push a verified change to `main`; the **Deploy SOP** GitHub Actions workflow validates and publishes `public/` to GitHub Pages. Media assets must stay below 90 MiB per file and the published directory below 800 MiB. Keep asset URLs relative so the site works at the independent domain root.

Use `node scripts/serve-static.mjs public 4186` for a local server with video byte-range and HLS support. The source PDF is preserved byte-for-byte, including its original authorship. The page publication date is retained from the supplied source.

## Media maintenance

The local `original/` directory contains the extracted archive and is excluded from Git. `scripts/prepare_media.py` creates the web video versions and posters without shortening or speeding up the content. It uses a local imageio-ffmpeg installation under `.tools/python/`. The supplied archive and original files are never overwritten. `scripts/prepare_page.py` documents the initial content conversion; normal website edits can be made directly to `public/index.html`, `public/style.css`, and `public/player.js`.

HLS.js 1.7.3 is bundled locally under its Apache-2.0 license in `public/vendor/`. Native HLS is used when the browser supports it; other compatible browsers use HLS.js after an explicit play request.

To roll back, revert the relevant commit and let the same workflow publish the reverted source. Do not rewrite shared history.
