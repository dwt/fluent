{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    python312
    python313
    python314
    pypy3
    uv
    git
  ];

  shellHook = ''
    unset PYTHONPATH
    export UV_PYTHON_DOWNLOADS=never
    export UV_PYTHON=$(which python3.14)
    uv sync --all-extras
    source .venv/bin/activate
  '';
}
