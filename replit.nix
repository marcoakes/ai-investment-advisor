{ pkgs }: {
  deps = [
    pkgs.python3Full
    pkgs.python3Packages.pip
    pkgs.python3Packages.setuptools
    pkgs.python3Packages.wheel
    pkgs.python3Packages.numpy
    pkgs.python3Packages.pandas
    pkgs.python3Packages.matplotlib
    pkgs.python3Packages.requests
    pkgs.python3Packages.scipy
    pkgs.tk
    pkgs.tcl
    pkgs.qhull
    pkgs.pkg-config
    pkgs.freetype
    pkgs.libpng
    pkgs.zlib
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.python3Packages.numpy.out
      pkgs.python3Packages.matplotlib.out
    ];
    PYTHONPATH = "$PWD";
    MPLBACKEND = "Agg";
  };
}