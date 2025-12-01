"""
Script Auxiliar para Usar Swing Electoral en Predicciones
Facilita la carga y aplicación del swing corregido
"""

import pandas as pd
import numpy as np

class SwingElectoral:
    """
    Clase para manejar swing electoral con coaliciones
    """
    
    def __init__(self, archivo_swing_coaliciones=None):
        """
        Inicializa con el archivo de swing con coaliciones
        """
        if archivo_swing_coaliciones is None:
            # Buscar el más reciente
            import glob
            archivos = glob.glob("outputs/swing/swing_con_coaliciones_*.csv")
            if not archivos:
                raise FileNotFoundError("No se encontró archivo de swing con coaliciones")
            archivo_swing_coaliciones = max(archivos)  # Más reciente
        
        print(f"[INFO] Cargando swing desde: {archivo_swing_coaliciones}")
        self.swing_df = pd.read_csv(archivo_swing_coaliciones)
        
        # Mapeo de entidades
        self.ESTADOS = {
            '01': 'Aguascalientes', '05': 'Coahuila', '10': 'Durango',
            '13': 'Hidalgo', '15': 'México', '20': 'Oaxaca',
            '23': 'Quintana Roo', '28': 'Tamaulipas'
        }
        
        print(f"[INFO] Swing cargado: {len(self.swing_df)} distritos")
    
    def obtener_swing(self, entidad, distrito):
        """
        Obtiene el swing de un distrito específico
        
        Args:
            entidad: Código de entidad (2 dígitos) o nombre
            distrito: Número de distrito federal
        
        Returns:
            dict con swing por partido y coaliciones, o None si no hay swing para ese estado
        """
        # Convertir nombre a código si es necesario
        if len(str(entidad)) > 2:
            # Comparación case-insensitive para nombres de estados
            entidad_upper = str(entidad).upper()
            entidad_codigo = next((k for k, v in self.ESTADOS.items() if v.upper() == entidad_upper), None)
            if not entidad_codigo:
                # Estado no está en la lista de 8 con elecciones locales - no hay swing
                return None
        else:
            entidad_codigo = str(entidad).zfill(2)
        
        # Verificar si el estado está en la lista de 8 estados con swing
        if entidad_codigo not in self.ESTADOS:
            # Estado fuera de los 8 - mantener votos originales
            return None
        
        # Buscar distrito (convertir entidad a int para comparar)
        row = self.swing_df[
            (self.swing_df['ENTIDAD'] == int(entidad_codigo)) & 
            (self.swing_df['DF_2021'] == int(distrito))
        ]
        
        if len(row) == 0:
            print(f"[WARN] No hay datos de swing para {self.ESTADOS.get(entidad_codigo, entidad_codigo)} DF-{distrito}")
            return None
        
        row = row.iloc[0]
        
        resultado = {
            'estado': row['NOMBRE_ESTADO'],
            'entidad': entidad_codigo,
            'df': int(row['DF_2021']),
            'anio_eleccion_local': int(row['AÑO_ELECCION']),
            'partidos': {
                'PAN': row['swing_PAN'] if row['swing_PAN'] > -99 else None,
                'PRI': row['swing_PRI'] if row['swing_PRI'] > -99 else None,
                'PRD': row['swing_PRD'] if row['swing_PRD'] > -99 else None,
                'PVEM': row['swing_PVEM'] if row['swing_PVEM'] > -99 else None,
                'PT': row['swing_PT'] if row['swing_PT'] > -99 else None,
                'MC': row['swing_MC'] if row['swing_MC'] > -99 else None,
                'MORENA': row['swing_MORENA'] if row['swing_MORENA'] > -99 else None,
            },
            'coaliciones': {
                'VA_X_MEX': row['swing_VA_X_MEX_PAN_PRI_PRD'] if pd.notna(row['swing_VA_X_MEX_PAN_PRI_PRD']) else None,
                'JUNTOS': row['swing_JUNTOS_PT_MORENA'] if pd.notna(row['swing_JUNTOS_PT_MORENA']) else None,
            }
        }
        
        return resultado
    
    def ajustar_votos(self, votos_2021, entidad, distrito, usar_coaliciones=True, 
                     factor_confianza=0.7):
        """
        Ajusta votos 2021 con swing
        
        Args:
            votos_2021: dict con votos por partido {partido: votos}
            entidad: Código de entidad o nombre
            distrito: Número de distrito federal
            usar_coaliciones: Si True, usa swing de coaliciones para PT+MORENA
            factor_confianza: Factor (0-1) para partidos con datos limitados
        
        Returns:
            dict con votos ajustados
        """
        swing_info = self.obtener_swing(entidad, distrito)
        
        if swing_info is None:
            print(f"[WARN] Sin datos de swing, retornando votos originales")
            return votos_2021.copy()
        
        votos_ajustados = {}
        estado = swing_info['estado']
        
        # PAN, PRI, PRD: usar individual (100% confianza)
        for partido in ['PAN', 'PRI', 'PRD']:
            swing = swing_info['partidos'][partido]
            if swing is not None:
                votos_ajustados[partido] = votos_2021[partido] * (1 + swing/100)
            else:
                votos_ajustados[partido] = votos_2021[partido]
        
        # PT + MORENA: usar coalición si está disponible
        if usar_coaliciones and swing_info['coaliciones']['JUNTOS'] is not None:
            swing_juntos = swing_info['coaliciones']['JUNTOS']
            
            # Evitar división por cero
            votos_coalicion_fed = votos_2021.get('PT', 0) + votos_2021.get('MORENA', 0)
            if votos_coalicion_fed > 0:
                votos_coalicion_ajust = votos_coalicion_fed * (1 + swing_juntos/100)
                
                # Distribuir proporcionalmente
                prop_pt = votos_2021.get('PT', 0) / votos_coalicion_fed
                votos_ajustados['PT'] = votos_coalicion_ajust * prop_pt
                votos_ajustados['MORENA'] = votos_coalicion_ajust * (1 - prop_pt)
            else:
                votos_ajustados['PT'] = 0
                votos_ajustados['MORENA'] = 0
        else:
            # Usar individual con factor de confianza
            for partido in ['PT', 'MORENA']:
                swing = swing_info['partidos'][partido]
                if swing is not None and swing > -99:
                    # Aplicar factor de confianza
                    votos_ajustados[partido] = votos_2021.get(partido, 0) * (
                        1 + (swing * factor_confianza)/100
                    )
                else:
                    votos_ajustados[partido] = votos_2021.get(partido, 0)
        
        # PVEM, MC: usar individual con factor de confianza (datos limitados)
        for partido in ['PVEM', 'MC']:
            swing = swing_info['partidos'][partido]
            if swing is not None and swing > -99:
                votos_ajustados[partido] = votos_2021.get(partido, 0) * (
                    1 + (swing * factor_confianza)/100
                )
            else:
                votos_ajustados[partido] = votos_2021.get(partido, 0)
        
        return votos_ajustados
    
    def estadisticas_por_estado(self):
        """
        Muestra estadísticas de swing por estado
        """
        print("\n" + "=" * 80)
        print("ESTADÍSTICAS DE SWING POR ESTADO")
        print("=" * 80)
        
        for estado in sorted(self.swing_df['NOMBRE_ESTADO'].unique()):
            df_estado = self.swing_df[self.swing_df['NOMBRE_ESTADO'] == estado]
            
            print(f"\n{estado} ({len(df_estado)} distritos):")
            
            # Swing de coaliciones
            swing_juntos = df_estado['swing_JUNTOS_PT_MORENA'].mean()
            swing_vxm = df_estado['swing_VA_X_MEX_PAN_PRI_PRD'].mean()
            
            if not pd.isna(swing_juntos):
                print(f"  Juntos (PT+MORENA):      {swing_juntos:+7.1f}%")
            if not pd.isna(swing_vxm):
                print(f"  Va por México (PAN+PRI+PRD): {swing_vxm:+7.1f}%")
            
            # Swing individual
            for partido in ['PAN', 'PRI', 'PRD']:
                col = f'swing_{partido}'
                datos = df_estado[df_estado[col] > -99][col]
                if len(datos) > 0:
                    print(f"  {partido:8s}:            {datos.mean():+7.1f}%")
    
    def exportar_para_integracion(self, output_file="outputs/swing/swing_para_api.csv"):
        """
        Exporta swing en formato simplificado para integración con API
        """
        columnas_export = [
            'ENTIDAD', 'DF_2021',
            'swing_PAN', 'swing_PRI', 'swing_PRD',
            'swing_PVEM', 'swing_PT', 'swing_MC', 'swing_MORENA',
            'swing_VA_X_MEX_PAN_PRI_PRD', 'swing_JUNTOS_PT_MORENA'
        ]
        
        df_export = self.swing_df[columnas_export].copy()
        
        # Reemplazar -100 por NaN
        for col in df_export.columns:
            if col.startswith('swing_'):
                df_export.loc[df_export[col] == -100.0, col] = np.nan
        
        df_export.to_csv(output_file, index=False)
        print(f"\n[OK] Swing exportado para API: {output_file}")
        print(f"     {len(df_export)} distritos")


def ejemplo_uso():
    """
    Ejemplo de cómo usar la clase SwingElectoral
    """
    print("=" * 80)
    print("EJEMPLO DE USO: SwingElectoral")
    print("=" * 80)
    
    # 1. Inicializar
    swing = SwingElectoral()
    
    # 2. Obtener swing de un distrito
    print("\n1. CONSULTAR SWING DE COAHUILA DF-3:")
    info = swing.obtener_swing('05', 3)
    if info:
        print(f"   Estado: {info['estado']}")
        print(f"   Elección local: {info['anio_eleccion_local']}")
        print(f"   Swing PT individual: {info['partidos']['PT']:+.1f}%")
        print(f"   Swing MORENA individual: {info['partidos']['MORENA']:+.1f}%")
        print(f"   Swing JUNTOS (PT+MORENA): {info['coaliciones']['JUNTOS']:+.1f}%")
    
    # 3. Ajustar votos
    print("\n2. AJUSTAR VOTOS 2021 CON SWING:")
    votos_2021 = {
        'PAN': 53858,
        'PRI': 60769,
        'PRD': 1038,
        'PVEM': 1810,
        'PT': 957,
        'MC': 1695,
        'MORENA': 53416
    }
    
    print("   Votos 2021 (federal):")
    for p, v in votos_2021.items():
        print(f"     {p}: {v:>8,}")
    
    votos_ajustados = swing.ajustar_votos(votos_2021, '05', 3, usar_coaliciones=True)
    
    print("\n   Votos ajustados con swing de COALICIÓN:")
    for p, v in votos_ajustados.items():
        cambio = ((v / votos_2021[p]) - 1) * 100 if votos_2021[p] > 0 else 0
        print(f"     {p}: {v:>8,.0f} ({cambio:+6.1f}%)")
    
    # 4. Estadísticas
    swing.estadisticas_por_estado()
    
    # 5. Exportar para API
    swing.exportar_para_integracion()
    
    print("\n" + "=" * 80)
    print("[OK] Ejemplo completado")
    print("=" * 80)


if __name__ == "__main__":
    ejemplo_uso()
