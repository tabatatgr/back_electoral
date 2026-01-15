"""
Script para ver resumen de resultados de distritación
"""
import pandas as pd

df = pd.read_csv('redistritacion/outputs/distritacion_Reforma_200-200_validacion.csv')

print('\n' + '='*60)
print('=== RESUMEN DISTRITACIÓN COMPLETA DE MÉXICO ===')
print('='*60)

print(f'\nTotal distritos creados: {len(df)}')
print(f'Estados procesados: {df["entidad_nombre"].nunique()}')

print(f'\n📊 CUMPLIMIENTO CONSTITUCIONAL:')
print(f'  ✓ Cumplen ±15%: {df["cumple_15pct"].sum()}/{len(df)} ({df["cumple_15pct"].mean()*100:.1f}%)')

print(f'\n📈 DESVIACIÓN POBLACIONAL:')
print(f'  Promedio: {df["desviacion_pct"].abs().mean():.3f}%')
print(f'  Mínima: {df["desviacion_pct"].abs().min():.3f}%')
print(f'  Máxima: {df["desviacion_pct"].abs().max():.3f}%')

print(f'\n👥 POBLACIÓN POR DISTRITO:')
print(f'  Promedio: {df["poblacion"].mean():,.0f}')
print(f'  Mínima: {df["poblacion"].min():,.0f}')
print(f'  Máxima: {df["poblacion"].max():,.0f}')

print(f'\n🗳️ SECCIONES POR DISTRITO:')
print(f'  Promedio: {df["secciones"].mean():.0f}')
print(f'  Mínima: {df["secciones"].min()}')
print(f'  Máxima: {df["secciones"].max()}')

print(f'\n🏘️ MUNICIPIOS POR DISTRITO:')
print(f'  Promedio: {df["municipios"].mean():.1f}')
print(f'  Mínimo: {df["municipios"].min()}')
print(f'  Máximo: {df["municipios"].max()}')

print(f'\n📍 TOP 5 ESTADOS CON MÁS DISTRITOS:')
top_estados = df.groupby('entidad_nombre')['distrito'].count().sort_values(ascending=False).head(5)
for estado, count in top_estados.items():
    pob_total = df[df['entidad_nombre'] == estado]['poblacion'].sum()
    print(f'  {estado}: {count} distritos ({pob_total:,.0f} habitantes)')

print(f'\n⚖️ VALIDACIÓN FINAL:')
if df['cumple_15pct'].all():
    print('  ✅ TODOS los distritos cumplen requisito constitucional ±15%')
else:
    print(f'  ⚠️ {(~df["cumple_15pct"]).sum()} distritos NO cumplen')

print('\n' + '='*60)
