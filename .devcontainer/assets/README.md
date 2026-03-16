# Pre-downloaded Assets

This devcontainer is intentionally configured to avoid network downloads in `Dockerfile`.
Place the required archives in this folder before building the image.

## Required files

- `node-v24.13.0-linux-amd64.tar.gz`
- `node-v24.13.0-linux-arm64.tar.gz`
  - Source: copied from existing workspace assets (official Node.js Linux archives).

## Notes

- Keep both architecture files in this folder.
- You can use newer patch versions; keep these exact filenames.
- Rename downloaded files to the names above.
- Optional but recommended: verify checksums/signatures from the vendor download pages.
