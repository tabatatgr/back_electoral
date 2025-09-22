import numpy as np
from engine.procesar_diputados_v2 import asignadip_v2

# Reconstruct arrays from previous debug output (order: partidos_base)
x = np.array([10049424., 6623752., 1449655., 4993902., 3254709., 6497404., 24286412.], dtype=float)
ssd = np.array([33, 9, 1, 58, 38, 1, 160], dtype=int)

try:
    resultado = asignadip_v2(
        x=x,
        ssd=ssd,
        indep=0,
        nulos=0,
        no_reg=0,
        m=172,  # rp seats roughly
        S=300,
        threshold=0.03,
        max_seats=300,
        max_pp=0.08,
        apply_caps=True,
        quota_method='hare',
        divisor_method='dhondt',
        seed=123,
        print_debug=True
    )
    print('Resultado seats:\n', resultado.get('seats'))
except Exception as e:
    import traceback
    print('Exception calling asignadip_v2:', e)
    traceback.print_exc()
