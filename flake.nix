{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/23.11";
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
        pkgs = import nixpkgs {
          inherit system;
        };
      in
      rec {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            (python310.withPackages (
              ps: with ps; [
                ipython
                jupyter
                jupyter-console
                jupyter-core
                jupyterlab
                keras
                matplotlib
                nbdime
                notebook
                numpy
                openpyxl
                pandas
                plotly
                scikit-learn
                scipy
                seaborn
                tensorflow
                xlrd
              ]
            ))
            git
          ];

          #shellHook = ''
          #  echo "Starting Jupyter Notebook..."
          #  jupyter notebook
          #'';
        };
      }
    );
}
