# SOP research website

Planned publication: https://scalable-online-posttraining.github.io/

Status: the previous project site has been withdrawn. The independent site is prepared but not yet deployed; it is awaiting creation of the `scalable-online-posttraining` GitHub organization under `tauteamhq`.

The `public/` directory is a self-contained static website. Its typography and layout follow the LWD, τ0-WM, and τ0-VLA research pages. It includes the original paper, three research figures, and 22 full-length videos. Two long timelapses use local HLS segments. No external font or video service is required.

## Domain migration

The target repository is `scalable-online-posttraining/scalable-online-posttraining.github.io`, managed by `tauteamhq`. After creating the organization, transfer and rename the existing `tauteamhq/sop` repository to the target, update the local remote, enable GitHub Pages with GitHub Actions, re-enable the publishing workflow, and deploy the verified source. This preserves the existing media and commit history. The previous Pages publication and automatic publishing remain disabled until the migration is ready.

## Validation and deployment

Run `python3 scripts/check_site.py` before publishing. Push a verified change to `main`; the **Deploy SOP** GitHub Actions workflow validates and publishes `public/` to GitHub Pages. Media assets must stay below 90 MiB per file and the published directory below 800 MiB. Keep asset URLs relative so the site works at the independent domain root.

Use `node scripts/serve-static.mjs public 4186` for a local server with video byte-range and HLS support. The source PDF is preserved byte-for-byte, including its original authorship. The page publication date is retained from the supplied source.

## Media maintenance

The local `original/` directory contains the extracted archive and is excluded from Git. `scripts/prepare_media.py` creates the web video versions and posters without shortening or speeding up the content. It uses a local imageio-ffmpeg installation under `.tools/python/`. The supplied archive and original files are never overwritten. `scripts/prepare_page.py` documents the initial content conversion; normal website edits can be made directly to `public/index.html`, `public/style.css`, and `public/player.js`.

HLS.js 1.7.3 is bundled locally under its Apache-2.0 license in `public/vendor/`. Native HLS is used when the browser supports it; other compatible browsers use HLS.js after an explicit play request.

To roll back, revert the relevant commit and let the same workflow publish the reverted source. Do not rewrite shared history.
