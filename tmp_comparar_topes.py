import pandas as pd

df_con = pd.read_csv('outputs/escenarios_morena_CON_TOPES_20251028_155004.csv')
df_sin = pd.read_csv('outputs/escenarios_morena_SIN_TOPES_20251028_160845.csv')

print("="*80)
print("COMPARACIÓN CON TOPES vs SIN TOPES - MORENA 2024")
print("="*80)

# Buscar mismo escenario en ambos
# 2024, 500 escaños, 50MR_50RP, CON coalición
r_con = df_con[(df_con['anio']==2024) & 
               (df_con['total_escanos']==500) & 
               (df_con['configuracion']=='50MR_50RP') & 
               (df_con['usar_coaliciones']=='CON')].iloc[0]

r_sin = df_sin[(df_sin['anio']==2024) & 
               (df_sin['escanos_totales']==500) & 
               (df_sin['config_mr_rp']=='50MR_50RP') & 
               (df_sin['coalicion']=='CON')].iloc[0]

print(f"\nEscenario: 2024, 500 escaños, 50MR_50RP, CON coalición")
print(f"\nCON TOPES:")
print(f"  MORENA: {r_con['morena_total']} escaños ({r_con['morena_pct_escanos']}%)")
print(f"  MR: {r_con['morena_mr']}, RP: {r_con['morena_rp']}")
print(f"  Votos: {r_con['morena_votos_pct']}%")

print(f"\nSIN TOPES:")
print(f"  MORENA: {r_sin['morena_total']} escaños ({r_sin['morena_pct']}%)")
print(f"  MR: {r_sin['morena_mr']}, RP: {r_sin['morena_rp']}")

print(f"\nDIFERENCIA: {r_sin['morena_total'] - r_con['morena_total']} escaños")

if r_sin['morena_total'] < r_con['morena_total']:
    print("❌ ERROR: SIN TOPES tiene MENOS escaños que CON TOPES!")
    print("   Esto NO tiene sentido - sin topes debería tener MÁS escaños")
elif r_sin['morena_total'] > r_con['morena_total']:
    print("✅ CORRECTO: SIN TOPES tiene MÁS escaños que CON TOPES")
else:
    print("⚠️ IGUAL: Ambos tienen los mismos escaños (puede ser normal si no hubo cap)")

# Comparar varios escenarios
print("\n" + "="*80)
print("RESUMEN DE MÚLTIPLES ESCENARIOS (2024)")
print("="*80)

for escanos in [400, 500, 600]:
    for config in ['50MR_50RP', '60MR_40RP', '75MR_25RP']:
        for coal in ['CON', 'SIN']:
            try:
                r_con = df_con[(df_con['anio']==2024) & 
                               (df_con['total_escanos']==escanos) & 
                               (df_con['configuracion']==config) & 
                               (df_con['usar_coaliciones']==coal)].iloc[0]
                
                r_sin = df_sin[(df_sin['anio']==2024) & 
                               (df_sin['escanos_totales']==escanos) & 
                               (df_sin['config_mr_rp']==config) & 
                               (df_sin['coalicion']==coal)].iloc[0]
                
                diff = r_sin['morena_total'] - r_con['morena_total']
                status = "✅" if diff >= 0 else "❌"
                
                print(f"{status} {escanos} | {config} | {coal}: CON={r_con['morena_total']} SIN={r_sin['morena_total']} DIFF={diff:+d}")
            except:
                pass
