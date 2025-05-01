from pathlib import Path
import pandas as pd
import pdb
import re

pd.set_option('display.max_rows', 500)

NaN = float('NaN')

root = Path("inputs/")

def load():
    products = pd.read_csv(
        root / "products anonymised.csv",
        encoding="utf-8",
        encoding_errors="replace",
        on_bad_lines="skip",
        low_memory=False,
    )
    categories = pd.read_csv(
        root / "categories anonymised.csv",
        encoding="utf-8",
        encoding_errors="replace",
        on_bad_lines="skip",
        low_memory=False,
    )
    #food_products.merge(food_categories, on="product_id", how="left")
    return products, categories

def clean_ingredients(string):
    orig_string = string
    # Strip alergy advice. Assume this occurs at the end.
    string = str(string)
    string = re.sub(r'(for\W)?all?erg(y|en).*', '', string, flags=re.IGNORECASE)
    string = re.sub(r'ingredients:? ?', '', string, flags=re.IGNORECASE)
    string = re.sub(r'\(([\d\.]+%)\)', r'\1', string)
    segments = re.split(r';|,|(\.\s)|\[|\]|\(|\)', string)
    ingredients = []
    for segment in segments:
        if segment is None: continue
        pattern = r'\(?[\d\.]+%\)'
        ingredient_string = re.sub(pattern, '', segment).strip().lower()
        if ingredient_string == 'nan':
            continue
        percent_match = re.findall(pattern, segment)
        #if len(percent_match) >= 2:
        #    print(f'Multiple percents found: "{segment}" ("{orig_string}")')
        if len(percent_match) == 1:
            try:
                percent_num = float(re.sub(r'[%\(\)]','',percent_match[0])) / 100.0
            except:
                print(f'Exception in ingredient: "{segment}" ("{orig_string}")')
                percent_num = NaN
        else:
            percent_num = NaN
        ingredients.append((ingredient_string, percent_num))
    return ingredients

def make_ingredients_df(products):
    products['ingredient_list'] = products['ingredients_text'].map(clean_ingredients)
    ingredients = products.explode('ingredient_list')
    ingredients[['ingredient', 'quantity']] = pd.DataFrame(ingredients['ingredient_list'].tolist(), index=ingredients.index)
    ingredients = ingredients[['product_id', 'ingredient', 'quantity']]
    return ingredients

def lookup_sci_unit(unit_raw, default_unit):
    unit_map = {
        "g" : 1e-3,
        "gr" : 1e-3,
        "gg" : 1e-3,
        "grams" : 1e-3,
        "gri" : 1e-3,
        "g/ml" : 1e-3, # this might not be right. Make NA?
        "mg" : 1e-6,
        "µg" : 1e-9,
        "ug" : 1e-9,
        "kg" : 1e0,

        # Effectively zero.
        "trace" : 0.0,
        "traceg" : 0.0,
        "traceamounts" : 0.0,
        "traces" : 0.0,
        "nil" : 0.0,
        "nilg" : 0.0,
        "zero" : 0.0,
        "belowg" : 0.0,
        "lessthang" : 0.0,
        "ltgri" : 0.0,
        "none" : 0.0,

        "kj" : 1e3,
        "kjoules" : 1e3,
        "kcal" : 4184,
        "cal" : 4184, # cal colloqually means kcal.

        # these are not interpretable. Throw them away to avoid polluting the data.
        "notlabelled": NaN,
        "na" : NaN,
        "nan" : NaN,
        "nang" : NaN,
    }

    unit_raw = unit_raw.strip().lower()
    if unit_raw in unit_map:
        return unit_map[unit_raw]
    else:
        print(f'No match for unit "{unit_raw}"')
        return default_unit

def clean_sci_quant(string, column, default_mult):
    orig_string = string
    string = str(string).lower()
    if string == 'nan':
        return NaN
    quant_match = re.findall(r'(\d+(\.\d+)?)',  string)
    unit_list = re.findall(r'[A-Za-z]+', string)

    # If they are equal lengths then it's probably the same quantity in differnt units.
    if len(quant_match) >= 2 and len(quant_match) != len(unit_list):
        print(f'Multiple quants found in item in column "{column}" "{orig_string}"')
    if len(quant_match) >= 1:
        try:
            quant = float(quant_match[0][0])
        except:
            print(f'Exception quant "{quant_match[0][0]}": "{column}" "{orig_string}"')
            quant = NaN
    else:
        print(f'No quant found: "{column}" "{orig_string}"')
        quant = NaN
    if len(unit_list) >= 1:
        unit_mult = lookup_sci_unit(unit_list[0], default_mult)
        if unit_mult is None:
            print('Lookup failed for "{orig_string}"')
            unit_mult = default_mult
    else:
        #print(f'No unit specified for "{column}" "{orig_string}"')
        unit_mult = default_mult # Assume default unit

    print(f'{column} {orig_string} -> {unit_list} ({unit_mult}), {quant}')
    return unit_mult * quant

def mult_serving(row):
    unit = str(row['serving_unit']).lower().strip()
    if unit == 'nan' or unit == '':
        mult = 0.001
    else:
        mult = lookup_sci_unit(unit, 0.001)

    if row['serving_value'].isna():
        return NaN
    else:
        try:
            return float(row['serving_value']) * mult
        except:
            return NaN

def clean(products, categories):
    #cols = ['product_id', 'snapshot_id', 'product_list_name', 'product_name', 'url',
    #    'ingredients_text', 'energy_per_100', 'fat_per_100',
    #    'saturates_per_100', 'salt_per_100', 'sugar_per_100',
    #    'carbohydrate_per_100', 'protein_per_100', 'fibre_per_100', 'serving',
    #    'serving_data', 'serving_value', 'serving_unit', 'Retailer', 'name',
    #    'main_category', 'department', 'aisle', 'shelf'],

    #sci_cols = ['energy_per_100', 'fat_per_100', 'saturates_per_100', 'salt_per_100', 'sugar_per_100', 'carbohydrate_per_100', 'protein_per_100', 'fibre_per_100']
    #serving_cols = ['serving', 'serving_data', 'serving_value', 'serving_unit']

    ingredients = make_ingredients_df(products)
    products['energy_per_100'] = products['energy_per_100'].map(lambda string: clean_sci_quant(string, 'energy_per_100', 1e3)) # kJ
    products['fat_per_100'] = products['fat_per_100'].map(lambda string: clean_sci_quant(string, 'fat_per_100', 1e-3))
    products['saturates_per_100'] = products['saturates_per_100'].map(lambda string: clean_sci_quant(string, 'saturates_per_100', 1e-3))
    products['salt_per_100'] = products['salt_per_100'].map(lambda string: clean_sci_quant(string, 'salt_per_100', 1e-3))
    products['sugar_per_100'] = products['sugar_per_100'].map(lambda string: clean_sci_quant(string, 'sugar_per_100', 1e-3))
    products['carbohydrate_per_100'] = products['carbohydrate_per_100'].map(lambda string: clean_sci_quant(string, 'carbohydrate_per_100', 1e-3))
    products['protein_per_100'] = products['protein_per_100'].map(lambda string: clean_sci_quant(string, 'protein_per_100', 1e-3))
    products['fibre_per_100'] = products['fibre_per_100'].map(lambda string: clean_sci_quant(string, 'fibre_per_100', 1e-3))

    return products, categories, ingredients
