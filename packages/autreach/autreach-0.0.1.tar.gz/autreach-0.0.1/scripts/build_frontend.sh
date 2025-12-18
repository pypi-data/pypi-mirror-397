#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STUDIO_UI_DIR="$PROJECT_ROOT/studio-ui"
DIST_DIR="$STUDIO_UI_DIR/dist"

if [ ! -d "$STUDIO_UI_DIR" ]; then
    echo "Error: $STUDIO_UI_DIR does not exist" >&2
    exit 1
fi

echo "Building frontend in $STUDIO_UI_DIR..."

cd "$STUDIO_UI_DIR"
pnpm build

if [ ! -d "$DIST_DIR" ]; then
    echo "Error: Build output directory $DIST_DIR was not created" >&2
    exit 1
fi

if [ ! -f "$DIST_DIR/index.html" ]; then
    echo "Error: $DIST_DIR/index.html was not created" >&2
    exit 1
fi

echo "✓ Frontend built successfully in $DIST_DIR"
echo "✓ API can now serve the frontend from studio-ui/dist"

