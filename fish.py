from pathlib import Path
import pandas as pd
import pdb
import re

pd.set_option('display.max_rows', 500)

NaN = float('NaN')

root = Path("inputs/")

def load():
    fish_env_info = pd.read_csv(
        root / "fish_env_info.csv",
        encoding="utf-8",
        encoding_errors="replace",
        on_bad_lines="skip",
        low_memory=False
    )
    fish_weighting = pd.read_csv(
        root / "fish_weighting.csv",
        encoding="utf-8",
        encoding_errors="replace",
        on_bad_lines="skip",
        low_memory=False
    )
    fish_matching = pd.read_csv(
        root / "fish_matching.csv",
        encoding="utf-8",
        encoding_errors="replace",
        on_bad_lines="skip",
        low_memory=False
    )
    return fish_env_info, fish_weighting, fish_matching
