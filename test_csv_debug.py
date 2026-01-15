"""Debug del CSV metadata"""
import pandas as pd
from io import StringIO
import datetime

# Simular exportación
estados_por_partido = {
    'MORENA': ['CDMX', 'MEXICO', 'JALISCO'],
    'PAN': ['GUANAJUATO', 'QUERETARO'],
    'PRI': ['COAHUILA']
}

datos = []
for partido, estados in estados_por_partido.items():
    for estado in estados:
        datos.append({
            'estado': estado,
            'partido_ganador': partido,
            'senadores_mr': 2
        })

df = pd.DataFrame(datos)

# Agregar metadata
metadata_rows = [
    {'estado': '# Escenario: Test_Export', 'partido_ganador': '', 'senadores_mr': ''},
    {'estado': '# Descripción: Test de exportación', 'partido_ganador': '', 'senadores_mr': ''},
    {'estado': f'# Fecha: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 'partido_ganador': '', 'senadores_mr': ''},
    {'estado': '# ---', 'partido_ganador': '', 'senadores_mr': ''},
]
df_metadata = pd.DataFrame(metadata_rows)
df_final = pd.concat([df_metadata, df], ignore_index=True)

# Convertir a CSV
csv_buffer = StringIO()
df_final.to_csv(csv_buffer, index=False, encoding='utf-8')
csv_content = csv_buffer.getvalue()

print("="*80)
print("CSV COMPLETO:")
print("="*80)
print(csv_content)
print("="*80)

# Ahora parsear
metadata = {}
lineas_datos = []

print("\nPROCESANDO LÍNEAS:")
for i, linea in enumerate(csv_content.split('\n')):
    print(f"  Línea {i}: '{linea[:60]}...' (empieza con #: {linea.strip().startswith('#')})")
    linea_limpia = linea.strip()
    if linea_limpia.startswith('#'):
        contenido = linea_limpia[1:].strip()
        if ':' in contenido:
            key, value = contenido.split(':', 1)
            # Limpiar comas finales del CSV
            value_limpio = value.strip().rstrip(',')
            metadata[key.strip()] = value_limpio
            print(f"    -> Metadata: {key.strip()} = {value_limpio}")
    else:
        if linea_limpia:
            lineas_datos.append(linea)

print("\n" + "="*80)
print("METADATA EXTRAÍDA:")
print("="*80)
for k, v in metadata.items():
    print(f"  '{k}': '{v}'")

print("\n" + "="*80)
print("RESULTADO:")
print("="*80)
print(f"  Escenario encontrado: '{metadata.get('Escenario')}'")
print(f"  ¿Es igual a 'Test_Export'? {metadata.get('Escenario') == 'Test_Export'}")
