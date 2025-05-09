{pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
  packages = [
    (pkgs.python313.withPackages (python313Packages: [
      python313Packages.discordpy
      python313Packages.rich
      python313Packages.debugpy # for debugging
    ]))
  ];
}
