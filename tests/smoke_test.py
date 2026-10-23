# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
"""Smoke test: runs every script on the demo logo and checks that each one finishes and writes what it promises.
It does not judge how the results look; open the preview images for that.

Usage: python tests/smoke_test.py [--keep out-folder] [--upscale]
  --keep     keep the results in this folder (default: a temporary folder, removed afterwards)
  --upscale  also run upscale.py (needs the optional upscale setup; takes a few minutes on a CPU)
Run it with the Python from setup_env.sh, or any Python with requirements.txt installed and Chromium for Playwright.
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / 'skills' / 'logo-repolish' / 'scripts'

ap = argparse.ArgumentParser()
ap.add_argument('--keep')
ap.add_argument('--upscale', action='store_true')
args = ap.parse_args()

out = Path(args.keep) if args.keep else Path(tempfile.mkdtemp(prefix='logo-repolish-test-'))
if args.keep and out.exists() and any(out.iterdir()):
    raise SystemExit(f'{out} is not empty; choose a new folder')
out.mkdir(parents=True, exist_ok=True)
failures = []


def run(name, cmd, expect=()):
    t0 = time.time()
    res = subprocess.run([sys.executable, *map(str, cmd)], capture_output=True, text=True)
    missing = [str(p) for p in expect if not Path(p).exists()]
    ok = res.returncode == 0 and not missing
    print(f'{"ok  " if ok else "FAIL"} {name} ({time.time() - t0:.1f}s)')
    if not ok:
        failures.append(name)
        print(res.stdout[-2000:], res.stderr[-2000:], sep='\n')
        if missing:
            print('missing:', *missing, sep='\n  ')
    return res.stdout


src, svg = out / 'demo-logo.png', out / 'demo-logo.svg'
run('demo logo', [ROOT / 'examples' / 'make_demo_logo.py', src], [src])
run('vectorize', [SCRIPTS / 'vectorize.py', src, svg, '--title', 'Example'], [svg])
text = run('compare', [SCRIPTS / 'compare.py', src, svg, out / 'check'], [out / 'check-diff.png', out / 'check-zoom.png'])
m = re.search(r'missing ([\d.]+)%, added ([\d.]+)%', text)
if m and float(m.group(1)) + float(m.group(2)) > 5:
    failures.append('compare: the vector differs from the source on more than 5% of the ink')
    print(text)
run('audit', [SCRIPTS / 'audit.py', svg, out / 'audit'], [out / 'audit' / f for f in ('audit.md', 'small-sizes.png', 'tight-gaps.png')])
run('export_kit', [SCRIPTS / 'export_kit.py', svg, '--out', out / 'kit', '--name', 'example'],
    [out / 'kit' / 'preview.png', out / 'kit' / 'svg' / 'example.svg', out / 'kit' / 'ico' / 'favicon.ico'])
run('lockups', [SCRIPTS / 'lockups.py', svg, '--out', out / 'lockup', '--text', 'EXAMPLE'], [out / 'lockup' / 'preview.png'])
run('icons', [SCRIPTS / 'icons.py', svg, '--out', out / 'icons'],
    [out / 'icons' / f for f in ('favicon.svg', 'favicon.ico', 'apple-touch-icon.png', 'icon-maskable-512.png')])
run('profiles', [SCRIPTS / 'profiles.py', svg, '--out', out / 'profiles', '--palettes', 'navy-white,ink-brand,white-brand',
                 '--brand-solid'], [out / 'profiles' / 'preview-all.png'])
run('covers', [SCRIPTS / 'covers.py', svg, '--out', out / 'covers', '--headline', 'Example Co',
               '--subline', 'Covers built from the logo mark', '--url', 'https://example.com/'],
    [out / 'covers' / f'cover-{p}-guides.png' for p in ('linkedin-company', 'linkedin-personal', 'x', 'facebook', 'youtube')])
if args.upscale:
    small = out / 'demo-small.png'
    run('demo logo, small', [ROOT / 'examples' / 'make_demo_logo.py', small, '--size', '256'], [small])
    run('upscale', [SCRIPTS / 'upscale.py', small, out / 'demo-small-4x.png'], [out / 'demo-small-4x.png'])

print()
if failures:
    print(f'{len(failures)} failed: {", ".join(failures)}. Results kept in {out}')
    sys.exit(1)
print(f'all passed. Results in {out}' if args.keep else 'all passed')
if not args.keep:
    shutil.rmtree(out)
