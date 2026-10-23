#!/usr/bin/env bash
# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
# One-time setup for the logo-repolish scripts, in a private virtual environment (nothing is installed system-wide).
#
#   bash setup_env.sh              core: Pillow, NumPy, SciPy, scikit-image, fontTools, Playwright + Chromium
#   bash setup_env.sh --upscale    also the optional upscaler: PyTorch (CPU), spandrel, RealESRGAN_x4plus model
#
# Location: $LOGO_REPOLISH_HOME, default ~/.cache/logo-repolish. Afterwards run the scripts with
#   ~/.cache/logo-repolish/venv/bin/python scripts/<script>.py ...
# Everything runs locally. The only downloads are the packages, the Chromium build and (with --upscale) the model.
set -euo pipefail

HOME_DIR="${LOGO_REPOLISH_HOME:-$HOME/.cache/logo-repolish}"
VENV="$HOME_DIR/venv"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
  python3 -m venv "$VENV"
fi
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet pillow numpy scipy scikit-image fonttools brotli playwright

# Chromium renders the SVGs exactly as browsers do. A system Chrome is used as a fallback if this download fails.
"$PY" -m playwright install chromium || echo "Chromium download failed; the scripts will try a system Chrome instead."

if [ "${1:-}" = "--upscale" ]; then
  "$PY" -m pip install --quiet torch torchvision --index-url https://download.pytorch.org/whl/cpu
  "$PY" -m pip install --quiet spandrel
  mkdir -p "$HOME_DIR/models"
  MODEL="$HOME_DIR/models/RealESRGAN_x4plus.pth"
  if [ ! -f "$MODEL" ]; then
    curl -fL --retry 3 -o "$MODEL.part" \
      https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
    mv "$MODEL.part" "$MODEL"
  fi
fi

"$PY" - <<'EOF'
import importlib
for m in ('PIL', 'numpy', 'scipy', 'skimage', 'fontTools', 'playwright'):
    importlib.import_module(m)
print('logo-repolish environment ready')
EOF
echo "Python: $PY"
