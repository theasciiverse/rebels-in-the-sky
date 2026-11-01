# Changes from upstream

This is the Asciiverse packaging of Rebels in the Sky 1.8.1
(GPL-3.0-or-later) by Alessandro Ricottone
(github.com/ricott1/rebels-in-the-sky). `main` is upstream's `main` at
their `v1.8.1` tag, with their history; the `upstream` remote points there.

## The game

Unchanged. Built from Cargo.lock with upstream's default features: audio
(internet radio through rodio) on, no relayer, no SSH server.

## Packaging

- `.github/workflows/release.yml` (new): builds the av archives on a tag,
  Linux (glibc, ALSA), macOS and Windows.
- `.github/workflows/deploy-ubuntu.yml` (removed): upstream's release job
  also fires on `v*.*.*` tags, so on our `v1.8.1-av.1` it would have
  published its own archive into our release.
- `asciiverse/record-preview.py` (new): records the catalog preview at
  160x48 with a pilot that reads the screen through pyte; the kept take is
  `asciiverse/rebels-in-the-sky.cast`.

## Not changed

- No system packages (.deb etc.): Arch and MacPorts already package it.
- The game checks crates.io for a newer version once a day and says so in
  its UI; with av, updates come through av.
- The interface is laid out for 160x48. It shrinks to smaller windows, but
  at 100x30 parts are cut off, among them the Challenge button.
