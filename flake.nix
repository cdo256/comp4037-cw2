{
  description = "COMP4037 CW2";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python313;
        pythonPackages = python.pkgs;
        inputs = with pythonPackages; [
            ipython
            jupyter
            matplotlib
            nbdime
            numpy
            openpyxl
            pandas
            scikit-learn
            scipy
            seaborn
            xlrd
            plotly
        ];
      in
      {
        devShells.default = pkgs.mkShell {
          packages = inputs;
        };

        packages.default = pkgs.stdenv.mkDerivation {
          pname = "python-analysis-script";
          version = "0.1.0";

          src = ./.; # assuming your script is in the root

          buildInputs = inputs;
          installPhase = ''
            mkdir -p $out/bin
            cp your_script.py $out/bin/
            echo '#!/bin/sh' > $out/bin/run-script
            echo '${python.interpreter} $out/bin/main.py "$@"' >> $out/bin/run-script
            chmod +x $out/bin/run-script
          '';
        };
      }
    );
}
