import glob
import pandas as pd

ZEN = "".join(chr(0xff01 + i) for i in range(94))
HAN = "".join(chr(0x21 + i) for i in range(94))
HAN2ZEN = str.maketrans(HAN, ZEN)

excel_files = glob.glob('*.xlsx')

general_name = set([])
product_name = set([])

for excel_file in excel_files:
    df = pd.read_excel(excel_file)
    general_name = general_name.union(set(df['成分名']))
    product_name = product_name.union(set(df['品名']))

general_name = set([x.replace(' ', '').replace('　', '') for x in general_name])
product_name = set([x.replace(' ', '').replace('　', '') for x in product_name])

new_general_name = []
new_product_name = []

for each in general_name:
    if len(each) < 36:
        new_general_name.append(each)
    else:
        new_general_name.append(each[:25])
        new_general_name.append(each[-25:])

for each in product_name:
    if len(each) < 30:
        for i in range(1, 13):
            with_header = f'［{str(i).translate(HAN2ZEN)}］{each}'
            new_product_name.append(with_header)
    elif len(each) > 35:
        new_product_name.append(each[:25])
        new_product_name.append(each[-25:])
    else:
        new_product_name.append(each)

all_names = set(new_general_name) | set(new_product_name)

with open('texts.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_names))

with open('dicts.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(set(''.join(all_names))))
