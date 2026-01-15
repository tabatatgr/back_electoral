import pandas as pd

df = pd.read_csv('redistritacion/outputs/comparacion_reforma_200_200_vs_baseline.csv')

print('\n' + '='*80)
print('🎉 RESULTADOS FINALES: REDISTRITACIÓN 200-200 🎉')
print('='*80)

print('\n📊 COMPARACIÓN BASELINE (300-200) vs REFORMA (200-200):\n')
print(df.to_string(index=False))

print('\n' + '─'*80)
print(f'✓ Total Baseline (300 MR + 200 RP): {df["BASELINE_TOT"].sum()} escaños')
print(f'✓ Total Reforma (200 MR + 200 RP): {df["REFORMA_TOT"].sum()} escaños')

print('\n📈 CAMBIOS SIGNIFICATIVOS:')
cambios_significativos = df[df['DIFF_TOT'].abs() > 5].sort_values('DIFF_TOT', ascending=False)
for _, row in cambios_significativos.iterrows():
    signo = '+' if row['DIFF_TOT'] > 0 else ''
    print(f"  {row['PARTIDO']}: {signo}{row['DIFF_TOT']} ({signo}{row['DIFF_MR']} MR, {signo}{row['DIFF_RP']} RP)")

print('\n' + '='*80)
