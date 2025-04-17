{pkgs}: {
  deps = [
    pkgs.pango
    pkgs.harfbuzz
    pkgs.glib
    pkgs.ghostscript
    pkgs.fontconfig
    pkgs.wget
    pkgs.unzip
    pkgs.librsvg
    pkgs.freetype
    pkgs.glibcLocales
    pkgs.postgresql
    pkgs.openssl
  ];
}
