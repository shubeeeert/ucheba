# Çàãðóçêà è ïîäãîòîâêà òèïîâ
import numpy as np
from numpy.lib import recfunctions as rfn
import os

# Îïðåäåëåíèå ñòðóêòóðèðîâàííîãî òèïà äàííûõ
dtype = np.dtype([
    ('ts', np.int32),
    ('filter_id', np.int16),
    ('turb', np.float32),
    ('ph', np.float32),
    ('cl', np.float32),
    ('flow', np.float32)
])

# ×òåíèå ôàéëà
data = np.genfromtxt('/content/drive/MyDrive/data.csv', delimiter=',', skip_header=1, dtype=dtype, encoding='utf-8')

n_rows = data.shape[0]
mem_bytes = data.nbytes
mem_mb = mem_bytes / (1024**2)
print(f'Êîëè÷åñòâî ñòðîê: {n_rows}')
print(f'Îáúåì ïàìÿòè: {mem_bytes} áàéò ({mem_mb:.2f} ÌÁ)')

# Ïîäñ÷åò NaN è Inf
fields = ['turb', 'ph', 'cl', 'flow']
total_elements = n_rows * len(fields)
arr_2d = rfn.structured_to_unstructured(data[fields])
bad_mask = ~np.isfinite(arr_2d)
bad_count = np.sum(bad_mask)

ratio = bad_count / total_elements
if ratio > 0.03:
    print(f'ÂÍÈÌÀÍÈÅ: Äîëÿ íåêîððåêòíûõ çíà÷åíèé (NaN/Inf) = {ratio:.2%} (>3%)')
else:
    print(f'Äîëÿ íåêîððåêòíûõ çíà÷åíèé = {ratio:.2%} (â ïðåäåëàõ íîðìû)')

np.save('/content/data_step1.npy', data)