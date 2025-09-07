{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
        {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            dotnetCorePackages.sdk_8_0_3xx
            jdk11
            maven
            python313
            python313Packages.pandas
            python313Packages.seaborn
            python313Packages.matplotlib
            python313Packages.numpy
            jupyter
          ];
        };
      });
}
