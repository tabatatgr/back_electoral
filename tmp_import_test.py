import sys
sys.path.append('.')
try:
    from engine.kpi_utils import calcular_kpis_electorales, formato_seat_chart
    print('IMPORT_OK')
except Exception as e:
    print('IMPORT_ERROR', e)
