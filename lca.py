from pathlib import Path
import pandas as pd
import pdb
import re

pd.set_option('display.max_rows', 500)

NaN = float('NaN')

root = Path("inputs/")

def load():
    jp_lca = pd.read_csv(
        root / "jp_lca_dat.csv",
        encoding="utf-8",
        encoding_errors="replace",
        on_bad_lines="skip",
        low_memory=False
    )
    return jp_lca
