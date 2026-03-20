#!/usr/bin/env bash
# rebuild-venv.sh
# Run this on the HOST machine (Ubuntu), NOT inside Docker.
# Finds the best available Python 3, rebuilds the venv with glibc-native binaries.

set -e
cd "$(dirname "$0")"

# ── Step 1: Find Python ────────────────────────────────────────────────────
echo "[1/5] Locating Python 3 on host..."

PYTHON=""
for candidate in python3.12 python3.11 python3.10 python3 python; do
    if command -v "$candidate" &>/dev/null; then
        VER=$("$candidate" -c "import sys; print(sys.version_info[:2])" 2>/dev/null)
        MAJOR=$("$candidate" -c "import sys; print(sys.version_info[0])")
        MINOR=$("$candidate" -c "import sys; print(sys.version_info[1])")
        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON="$candidate"
            echo "    Found: $candidate ($VER)"
            break
        else
            echo "    Skipping $candidate (too old: $VER)"
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo ""
    echo "ERROR: No Python 3.10+ found on this machine."
    echo "Install it with:  sudo apt install python3.12 python3.12-venv"
    exit 1
fi

# ── Step 2: Ensure venv module is available ───────────────────────────────
echo "[2/5] Checking venv module..."
if ! "$PYTHON" -m venv --help &>/dev/null; then
    PYVER=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "ERROR: venv module missing. Install with:"
    echo "  sudo apt install python${PYVER}-venv"
    exit 1
fi
echo "    venv module OK"

# ── Step 3: Destroy old musl venv ─────────────────────────────────────────
echo "[3/5] Removing old venv (musl/Alpine binaries)..."
rm -rf venv

# ── Step 4: Create fresh venv + install deps ──────────────────────────────
echo "[4/5] Creating glibc-native venv..."
"$PYTHON" -m venv venv

echo "      Upgrading pip..."
venv/bin/pip install --upgrade pip --quiet

echo "      Installing requirements..."
venv/bin/pip install -r requirements.txt

# ── Step 5: Verify imports ────────────────────────────────────────────────
echo "[5/5] Verifying critical imports..."
venv/bin/python - <<'PYEOF'
import sys
print(f"  Python: {sys.version}")
import asyncssh;  print(f"  asyncssh: {asyncssh.__version__}")
import mcp;       print(f"  mcp: OK")
import yaml;      print(f"  pyyaml: OK")
import uvicorn;   print(f"  uvicorn: OK")

# Check that C extensions are glibc, not musl
import platform
libc = platform.libc_ver()
print(f"  libc: {libc}")
PYEOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Done. Venv rebuilt with host-native binaries."
echo "  Now restart Claude Desktop."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
