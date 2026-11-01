# Rebels in the Sky (Asciiverse packaging)

Rebels in the Sky 1.8.1 by Alessandro Ricottone, space pirates playing
basketball, Rust + Ratatui, with online play over libp2p. Packaged for the
Asciiverse catalog (id `rebels-in-the-sky`, binary `rebels`). Upstream is
active (github.com/ricott1/rebels-in-the-sky, remote `upstream`): don't
change the game; list anything we change in PATCHES.md.

- `origin` is to be github.com/theasciiverse/rebels-in-the-sky.
- Release: tag `v<upstream version>-av.<n>` (first: `v1.8.1-av.1`) and push
  it. For a new upstream release, merge its tag into `main`.
- Build: `cargo build --release --locked` (needs cmake and, on Linux,
  libasound2-dev).
- Saves go to the platform config dir (`directories`, org.frittura.rebels).
- Best at 160x48 (below that, parts of panels are cut off). The preview is
  recorded at 160x48 and cropped to 100x30 by the manifest.
- Preview: `python3 asciiverse/record-preview.py` (needs pyte); takes about
  a minute and leaves no processes behind.
