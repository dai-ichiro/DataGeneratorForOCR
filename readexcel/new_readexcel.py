import glob
import pandas as pd

max_len = 35

ZEN = "".join(chr(0xff01 + i) for i in range(94))
HAN = "".join(chr(0x21 + i) for i in range(94))
HAN2ZEN = str.maketrans(HAN, ZEN)

excel_files = glob.glob('*.xlsx')

product_name = set([])

for excel_file in excel_files:
    df = pd.read_excel(excel_file)
    product_name = product_name.union(set(df['品名']))

product_name = set([x.replace(' ', '').replace('　', '') for x in product_name])

new_product_name = []
        
for each in product_name:
    if len(each) < (max_len -3):
        for i in range(1, 13):
            with_header = f'［{str(i).translate(HAN2ZEN)}］{each}'
            new_product_name.append(with_header)
    elif len(each) > max_len:
        new_product_name.append(each[:max_len])
        new_product_name.append(each[-max_len:])
    else:
        new_product_name.append(each)

all_names = set(new_product_name)

with open(f'texts_max_len_{max_len}.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_names))

with open('dicts.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(set(''.join(all_names))))
