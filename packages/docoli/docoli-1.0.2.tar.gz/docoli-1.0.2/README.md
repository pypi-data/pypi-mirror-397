# dotlinker (doli)

`dotlinker` (CLI: `doli`) helps you persist and synchronize configuration across multiple systems by
linking local config paths to either:

- **chezmoi** (Git-based dotfiles management)
- **Nextcloud** (file-sync based persistence)

It is designed to be **simple**, **deterministic**, and **safe by default** (with timestamped backups).

## Features

- Default config path: `~/.config/dotlinker/config.yaml` (XDG-aware via `XDG_CONFIG_HOME`)
- Backends:
  - **chezmoi**: imports paths via `chezmoi add`
  - **cloud**: copies data to a destination directory, creates `.bak` backups, and links back with symlinks
- Unit tests via `unittest`
- Makefile target: `make test`

## Installation

```bash
pip install .
```

Or editable install for development:

```bash
pip install -e .
```

## Usage

Show help:

```bash
doli --help
doli
```

Add a mapping (non-interactive):

```bash
doli add -N zshrc -b chezmoi -s ~/.zshrc
doli add -N nvim  -b cloud   -s ~/.config/nvim -d ~/Nextcloud/dotfiles/.config/nvim
```

Run the linking/import process:

```bash
doli pull
```

Use a custom config path:

```bash
doli -c ./my-config.yaml add -N nvim -b cloud -s ~/.config/nvim -d ~/Nextcloud/dotfiles/.config/nvim
doli -c ./my-config.yaml pull
```

## Configuration format

`~/.config/dotlinker/config.yaml`

```yaml
mappings:
  - name: zshrc
    backend: chezmoi
    src: ~/.zshrc

  - name: nvim
    backend: cloud
    src: ~/.config/nvim
    dest: ~/Nextcloud/dotfiles/.config/nvim
```

### Notes

* For `backend: cloud`, `dest` is required.
* `cloud` creates timestamped backups:

  * destination backups: `dest.<timestamp>.bak`
  * source backups: `src.<timestamp>.bak`
* If `src` is already a symlink pointing to `dest`, `doli pull` is a NOOP.

## Development

Run tests:

```bash
make test
```

Run tests verbosely:

```bash
make test-verbose
```

## License

MIT License. See `LICENSE`.

## Author

Kevin Veen-Birkenbach
[https://www.veen.world/](https://www.veen.world/)
