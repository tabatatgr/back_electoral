import pandas as pd

df = pd.read_csv('outputs/comparativa_2021_vs_2024_CORREGIDO_20260106_135015.csv')

print("=" * 80)
print("ESCENARIO: MR 200 - PM 200 (2024)")
print("Deberíamos tener 200 MR + 200 PM = 400 total")
print("=" * 80)

# Filtrar solo 2024 y escenario MR 200 - PM 200, EXCLUYENDO coaliciones
df_esc = df[(df['Año']==2024) & (df['Escenario']=='MR 200 - PM 200') & (~df['Partido'].str.startswith('COALICIÓN', na=False))]

print("\nRESUMEN POR PARTIDO:")
print(df_esc[['Partido','Votos_%','MR','PM','RP','Total']].to_string(index=False))

print("\n" + "=" * 80)
print("TOTALES:")
total_mr = df_esc['MR'].sum()
total_pm = df_esc['PM'].sum()
total_rp = df_esc['RP'].sum()
total = df_esc['Total'].sum()

print(f"MR total: {total_mr}")
print(f"PM total: {total_pm}")
print(f"RP total: {total_rp}")
print(f"TOTAL: {total}")
print(f"\n¿Suma 400? {'✓ SÍ' if total == 400 else f'⚠️ NO - Faltan {400-total}'}")
print(f"¿MR+PM = 400? {'✓ SÍ' if total_mr + total_pm == 400 else f'⚠️ NO - {total_mr}+{total_pm}={total_mr+total_pm}'}")

print("\n" + "=" * 80)
print("VERIFICACIÓN DE TOPES (42.49% + 8% = 50.49% * 400 = 201 MAX):")
morena = df_esc[df_esc['Partido']=='MORENA'].iloc[0]
print(f"MORENA: MR={int(morena['MR'])}, PM={int(morena['PM'])}, Total={int(morena['Total'])}")
print(f"Tope: 201 escaños")
print(f"Estado: {'✓ OK' if morena['Total'] <= 201 else '⚠️ EXCEDE'}")
print(f"Espacio disponible: {201 - int(morena['MR'])} (después de MR)")
print(f"PM asignados: {int(morena['PM'])}")
print(f"¿PM <= Espacio? {'✓ SÍ' if morena['PM'] <= (201 - morena['MR']) else '⚠️ NO'}")
