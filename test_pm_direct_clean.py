"""
Test directo de PM sin servidor - verifica la lgica del motor
"""
import sys
sys.path.insert(0, '.')

from engine.procesar_diputados_v2 import procesar_diputados_v2

def test_pm_motor():
    """Test directo del motor con PM"""
    print("\n" + "="*80)
    print("TEST: Motor procesar_diputados_v2 con PM")
    print("="*80)
    
    # Parmetros de prueba
    path_parquet = "data/computos_diputados_2024.parquet"
    anio = 2024
    path_siglado = "data/siglado-diputados-2024.csv"
    
    print(f"\n Configuracin:")
    print(f"    Ao: {anio}")
    print(f"    Sistema: MR puro")
    print(f"    Total escaos: 300")
    print(f"    PM solicitado: 100")
    
    try:
        # Llamar al motor directamente
        resultado = procesar_diputados_v2(
            path_parquet=path_parquet,
            anio=anio,
            path_siglado=path_siglado,
            max_seats=300,
            sistema='mr',
            mr_seats=300,
            rp_seats=0,
            pm_seats=100,  #  CLAVE: 100 escaos de primera minora
            umbral=0.03,
            print_debug=True
        )
        
        print(f"\n Resultado:")
        print(f"    Keys en resultado: {list(resultado.keys())}")
        
        # Verificar que 'pm' est en el resultado
        if 'pm' in resultado:
            print(f"    Clave 'pm' presente en resultado!")
            
            mr_dict = resultado.get('mr', {})
            pm_dict = resultado.get('pm', {})
            rp_dict = resultado.get('rp', {})
            tot_dict = resultado.get('tot', {})
            
            total_mr = sum(mr_dict.values())
            total_pm = sum(pm_dict.values())
            total_rp = sum(rp_dict.values())
            total_escanos = sum(tot_dict.values())
            
            print(f"\n Totales:")
            print(f"    MR efectivo: {total_mr}")
            print(f"    PM: {total_pm}")
            print(f"    RP: {total_rp}")
            print(f"    Total: {total_escanos}")
            
            print(f"\n Top 5 partidos:")
            print(f"{'Partido':<15} {'MR':<8} {'PM':<8} {'RP':<8} {'Total':<8}")
            print("-" * 55)
            
            # Ordenar por total de escaos
            partidos_ordenados = sorted(tot_dict.items(), key=lambda x: x[1], reverse=True)[:5]
            for partido, total in partidos_ordenados:
                mr = mr_dict.get(partido, 0)
                pm = pm_dict.get(partido, 0)
                rp = rp_dict.get(partido, 0)
                print(f"{partido:<15} {mr:<8} {pm:<8} {rp:<8} {total:<8}")
            
            # Verificaciones
            print(f"\n Verificaciones:")
            if total_pm > 0:
                print(f"    PM asignado: {total_pm} escaos")
            else:
                print(f"    PM = 0 - no se asignaron escaos PM")
            
            if total_escanos == 300:
                print(f"    Total correcto: 300 escaos")
            else:
                print(f"     Total: {total_escanos} (esperado: 300)")
            
            # Verificar partidos con PM
            partidos_con_pm = {p: v for p, v in pm_dict.items() if v > 0}
            if partidos_con_pm:
                print(f"    {len(partidos_con_pm)} partidos tienen PM:")
                for partido, escanos in sorted(partidos_con_pm.items(), key=lambda x: x[1], reverse=True):
                    print(f"       {partido}: {escanos} PM")
            else:
                print(f"    Ningn partido tiene PM")
                
        else:
            print(f"    Clave 'pm' NO presente en resultado")
            print(f"   Keys disponibles: {list(resultado.keys())}")
        
        return resultado
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("Test directo del motor con PM")
    resultado = test_pm_motor()
    
    if resultado and 'pm' in resultado:
        total_pm = sum(resultado['pm'].values())
        if total_pm > 0:
            print(f"\nEXITO! PM funciona correctamente ({total_pm} escanos asignados)")
        else:
            print(f"\nPM devuelto pero con 0 escanos")
    else:
        print(f"\nTest fallo")
    
    print("\n" + "="*80)
