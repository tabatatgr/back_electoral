from engine.wrappers import run_simulacion
r = run_simulacion(anio=2024, camara='diputados', modelo='personalizado', sistema='mr', magnitud=123)
print('meta S=', r['meta']['S'])
print('meta m_mr=', r['meta']['m_mr'])
print('m_rp=', r['meta']['m_rp'])