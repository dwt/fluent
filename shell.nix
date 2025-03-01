{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python39
    python310
    python311
    python312
    python313
    pypy3
    uv
    git
  ];

  shellHook = ''
    unset PYTHONPATH
    export UV_PYTHON_DOWNLOADS=never
    export UV_PYTHON=$(which python3.13)
    uv sync
    source ./venv/bin/activate
  '';
}
