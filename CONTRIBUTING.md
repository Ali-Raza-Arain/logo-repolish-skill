# Contributing

Thank you for helping. Bug reports, platform size updates, better defaults and new tools are all welcome.

## Ground rules

- **Local only.** No tool may send a logo, or anything made from one, over the network. The only network use
  allowed is the one-time setup.
- **Never change a logo's colours or shape silently.** Tools may report, suggest and offer options; changes to
  the design happen only through explicit options the user chooses.
- **Never overwrite.** Tools write to new or empty folders, or refuse and explain, unless `--force` is passed.
- **Only shareable images.** Use the demo mark (`examples/make_demo_logo.py`) or images you have the right to
  share in issues, tests and docs. Never attach a client's or employer's logo.

## Development setup

```bash
bash skills/logo-repolish/scripts/setup_env.sh
PY=~/.cache/logo-repolish/venv/bin/python
$PY tests/smoke_test.py
```

## Before opening a pull request

1. Run `python tests/smoke_test.py` and make sure it passes. If you touched `upscale.py`, add `--upscale`.
2. Open the preview images from `python tests/smoke_test.py --keep /tmp/lr-check` and check that your change
   looks right, not just that it runs.
3. If the change affects the images in the README, rebuild them with
   `python tools/make_readme_images.py /tmp/lr-check`.
4. Update `docs/cli.md` for any new or changed option, and `CHANGELOG.md`.
5. If the skill's behaviour changes, update `skills/logo-repolish/SKILL.md`. Keep its description under 1024
   characters; `python tools/package_skill.py` checks that.
6. If you add a dependency, add it to `requirements.txt` (or `requirements-upscale.txt`) and to
   `skills/logo-repolish/scripts/setup_env.sh`, and list it in `THIRD_PARTY_NOTICES.md`.

## Style

- Python 3.10 or newer, standard library plus the listed dependencies.
- Each script is a self-contained command with a docstring that explains what it does and how to call it.
- Shared code goes in `scripts/common.py`.
- Messages to the user are plain sentences: what was written, where, and any warning.
- Documentation uses plain, concrete English in sentence case.

## Platform sizes

Social platforms change cover and profile sizes from time to time. To update one, change its entry in
`PLATFORMS` at the top of `covers.py`, update `references/platform-sizes.md`, and mention the platform's help
page you checked in the pull request.
