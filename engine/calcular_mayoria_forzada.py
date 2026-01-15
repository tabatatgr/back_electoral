"""
Calcula la configuración necesaria para forzar que un partido alcance
mayoría simple (201 escaños) o calificada (267 escaños).

IMPORTANTE: 
- Mayoría simple funciona en TODOS los escenarios
- Mayoría calificada SOLO funciona cuando aplicar_topes=False
  (porque con topes del 8%, el máximo es ~179 escaños para un partido con 42% votos)

Método:
1. Objetivo: 201 (simple) o 267 (calificada) escaños totales
2. Distribuir entre MR y RP de forma realista
3. Calcular votos necesarios para justificar ese RP
4. Retornar configuración lista para usar en POST /procesar/diputados

Autor: Sistema Electoral v2.0
Fecha: 2024
"""

import numpy as np
from typing import Dict, Optional, Literal


def calcular_mayoria_forzada(
    partido: str,
    tipo_mayoria: Literal["simple", "calificada"],
    mr_total: int = 300,
    rp_total: int = 100,
    aplicar_topes: bool = True,
    votos_base: Optional[Dict[str, float]] = None
) -> Dict:
    """
    Calcula la configuración para forzar una mayoría.
    
    Args:
        partido: Nombre del partido (ej: "MORENA", "PAN", "PRI")
        tipo_mayoria: "simple" (201) o "calificada" (267)
        mr_total: Total de distritos MR (default: 300)
        rp_total: Total de escaños RP (default: 100)
        aplicar_topes: Si se aplican topes del 8%
        votos_base: Distribución de votos actual (opcional, para calcular ajustes)
    
    Returns:
        Dict con:
        - viable: bool - si es posible alcanzar la mayoría
        - razon: str - explicación si no es viable
        - mr_distritos_manuales: str (JSON) - MR por partido
        - votos_custom: str (JSON) - % de votos ajustados
        - escanos_esperados: int - escaños que debería obtener
        - advertencias: List[str] - advertencias sobre la configuración
    """
    
    total_escanos = mr_total + rp_total
    objetivo = 201 if tipo_mayoria == "simple" else 267
    
    # Votos base default (si no se proporcionan)
    if votos_base is None:
        votos_base = {
            "MORENA": 38.0,
            "PAN": 22.0,
            "PRI": 18.0,
            "MC": 12.0,
            "PVEM": 6.0,
            "PT": 4.0
        }
    
    # Validar que el partido existe
    if partido not in votos_base:
        return {
            "viable": False,
            "razon": f"Partido '{partido}' no encontrado en distribución de votos"
        }
    
    # Validar viabilidad según tipo de mayoría y topes
    if tipo_mayoria == "calificada" and aplicar_topes:
        # Con topes del 8%, el máximo para un partido es:
        # max_escanos = floor((votos% + 8%) × total_escanos)
        # Para alcanzar 267: votos% + 8% >= 267/400 = 66.75%
        # votos% >= 58.75%
        
        votos_min_necesarios = (objetivo / total_escanos - 0.08) * 100
        
        return {
            "viable": False,
            "razon": f"Mayoría calificada (267 escaños) es IMPOSIBLE con topes del 8%. "
                    f"Requeriría {votos_min_necesarios:.1f}% de votos (históricamente inalcanzable). "
                    f"Para usar mayoría calificada, DESACTIVE los topes (aplicar_topes=False)",
            "sugerencia": "Desactivar topes de sobrerrepresentación",
            "votos_min_necesarios": votos_min_necesarios
        }
    
    # Calcular distribución MR/RP para alcanzar objetivo
    advertencias = []
    
    # Estrategia: Maximizar MR (más realista), complementar con RP
    # MR: Dar al partido un % alto pero creíble (60-80% de los distritos MR)
    # RP: Ajustar votos para que el RP proporcional complete el objetivo
    
    # Para mayoría simple: 60% de MR es realista
    # Para mayoría calificada (sin topes): necesita ~90% de MR
    if tipo_mayoria == "simple":
        pct_mr_objetivo = 65.0  # 65% de distritos MR
    else:
        pct_mr_objetivo = 90.0  # 90% de distritos MR (muy dominante)
        advertencias.append(
            f"Mayoría calificada requiere dominio extremo: {pct_mr_objetivo:.0f}% de distritos MR"
        )
    
    mr_ganados = int(mr_total * pct_mr_objetivo / 100)
    
    # RP necesario para completar objetivo
    rp_necesario = objetivo - mr_ganados
    
    # Validar que el RP necesario no exceda el disponible
    if rp_necesario > rp_total:
        return {
            "viable": False,
            "razon": f"Incluso ganando {mr_ganados}/{mr_total} distritos MR ({pct_mr_objetivo:.0f}%), "
                    f"faltan {rp_necesario - rp_total} escaños (solo hay {rp_total} RP disponibles)",
            "mr_ganados_max": mr_total,
            "rp_max": rp_total,
            "deficit": rp_necesario - rp_total
        }
    
    if rp_necesario < 0:
        # Si con MR ya alcanza, ajustar
        mr_ganados = objetivo
        rp_necesario = 0
        advertencias.append(
            f"Con {mr_ganados} distritos MR ya se alcanza el objetivo (no requiere RP)"
        )
    
    # Calcular % de votos necesario para justificar ese RP
    # RP proporcional = (votos% / 100) × rp_total
    # votos% = (rp_necesario / rp_total) × 100
    
    if rp_total > 0 and rp_necesario > 0:
        pct_votos_minimo_rp = (rp_necesario / rp_total) * 100
    else:
        pct_votos_minimo_rp = 0
    
    # Ajustar votos para ser realista Y suficiente
    # Para mayoría simple: al menos 40-45% es creíble
    # Para mayoría calificada sin topes: al menos 45-50%
    
    if tipo_mayoria == "simple":
        pct_votos_necesario = max(pct_votos_minimo_rp, 42.0)  # Mínimo 42% para ser creíble
    else:
        pct_votos_necesario = max(pct_votos_minimo_rp, 45.0)  # Mínimo 45% para calificada
    
    # Ajustar votos para no exceder 100% total
    # Dar al partido el % calculado, distribuir el resto proporcionalmente
    votos_ajustados = {}
    votos_resto_total = sum(v for p, v in votos_base.items() if p != partido)
    
    if votos_resto_total == 0:
        votos_resto_total = 100.0 - votos_base.get(partido, 0)
    
    # Asegurar que los votos del partido no excedan ~90% (realismo)
    pct_votos_necesario = min(pct_votos_necesario, 90.0)
    
    votos_ajustados[partido] = round(pct_votos_necesario, 2)
    votos_restantes = 100.0 - pct_votos_necesario
    
    # Distribuir el resto proporcionalmente entre otros partidos
    for p, v in votos_base.items():
        if p != partido:
            proporcion = v / votos_resto_total if votos_resto_total > 0 else 0
            votos_ajustados[p] = round(votos_restantes * proporcion, 2)
    
    # Ajuste final para que sume exactamente 100%
    suma_actual = sum(votos_ajustados.values())
    if suma_actual != 100.0:
        diff = 100.0 - suma_actual
        votos_ajustados[partido] += diff
        votos_ajustados[partido] = round(votos_ajustados[partido], 2)
    
    # Crear configuración de MR manuales (solo el partido objetivo)
    # Los demás partidos se distribuyen automáticamente
    mr_resto = mr_total - mr_ganados
    
    # Distribuir MR restantes proporcionalmente entre otros partidos
    mr_manuales = {partido: mr_ganados}
    
    votos_otros = {p: v for p, v in votos_ajustados.items() if p != partido}
    total_votos_otros = sum(votos_otros.values())
    
    mr_asignados = mr_ganados
    for p in sorted(votos_otros.keys(), key=lambda x: votos_otros[x], reverse=True):
        if mr_asignados >= mr_total:
            mr_manuales[p] = 0
        else:
            proporcion = votos_otros[p] / total_votos_otros if total_votos_otros > 0 else 0
            mr_partido = int(mr_resto * proporcion)
            mr_partido = min(mr_partido, mr_total - mr_asignados)
            mr_manuales[p] = mr_partido
            mr_asignados += mr_partido
    
    # Ajustar último partido para completar exactamente mr_total
    if mr_asignados < mr_total:
        ultimo_partido = [p for p in mr_manuales.keys() if p != partido][0]
        mr_manuales[ultimo_partido] += (mr_total - mr_asignados)
    
    # Verificar escaños esperados (cálculo aproximado)
    escanos_esperados_aprox = mr_ganados + int(rp_total * pct_votos_necesario / 100)
    
    # Advertencias adicionales
    if pct_votos_necesario > 60:
        advertencias.append(
            f"Requiere {pct_votos_necesario:.1f}% de votos (muy alto, poco realista)"
        )
    
    if mr_ganados / mr_total > 0.85:
        advertencias.append(
            f"Requiere ganar {mr_ganados}/{mr_total} distritos MR ({mr_ganados/mr_total*100:.0f}%) "
            f"- dominio extremo, históricamente improbable"
        )
    
    import json
    
    return {
        "viable": True,
        "partido": partido,
        "tipo_mayoria": tipo_mayoria,
        "objetivo_escanos": objetivo,
        "mr_distritos_manuales": json.dumps(mr_manuales),
        "votos_custom": json.dumps(votos_ajustados),
        "escanos_esperados": escanos_esperados_aprox,
        "detalle": {
            "mr_ganados": mr_ganados,
            "mr_total": mr_total,
            "pct_mr": round(mr_ganados / mr_total * 100, 1),
            "rp_esperado": rp_necesario,
            "rp_total": rp_total,
            "pct_votos": round(pct_votos_necesario, 2)
        },
        "advertencias": advertencias,
        "nota": (
            "Esta configuración FUERZA el resultado ajustando MR y votos. "
            f"El partido {partido} debería obtener ~{escanos_esperados_aprox} escaños "
            f"({mr_ganados} MR + ~{rp_necesario} RP)"
        )
    }


def ejemplo_uso():
    """Ejemplo de uso de la función."""
    
    print("="*100)
    print("EJEMPLO: Calcular configuración para mayoría forzada")
    print("="*100)
    
    # Ejemplo 1: Mayoría simple para MORENA (300-100 con topes)
    print("\n1. Mayoría SIMPLE para MORENA (300-100 CON TOPES)")
    print("-"*100)
    resultado = calcular_mayoria_forzada(
        partido="MORENA",
        tipo_mayoria="simple",
        mr_total=300,
        rp_total=100,
        aplicar_topes=True
    )
    
    if resultado["viable"]:
        print(f"✓ VIABLE")
        print(f"  Objetivo: {resultado['objetivo_escanos']} escaños")
        print(f"  MR ganados: {resultado['detalle']['mr_ganados']}/{resultado['detalle']['mr_total']} ({resultado['detalle']['pct_mr']}%)")
        print(f"  RP esperado: {resultado['detalle']['rp_esperado']}/{resultado['detalle']['rp_total']}")
        print(f"  Votos necesarios: {resultado['detalle']['pct_votos']}%")
        print(f"\n  Configuración para POST /procesar/diputados:")
        print(f"    mr_distritos_manuales: {resultado['mr_distritos_manuales']}")
        print(f"    votos_custom: {resultado['votos_custom']}")
        if resultado.get("advertencias"):
            print(f"\n  ⚠️  Advertencias:")
            for adv in resultado["advertencias"]:
                print(f"    - {adv}")
    else:
        print(f"✗ NO VIABLE: {resultado['razon']}")
    
    # Ejemplo 2: Mayoría calificada para MORENA (300-100 CON topes) - debería fallar
    print("\n\n2. Mayoría CALIFICADA para MORENA (300-100 CON TOPES)")
    print("-"*100)
    resultado = calcular_mayoria_forzada(
        partido="MORENA",
        tipo_mayoria="calificada",
        mr_total=300,
        rp_total=100,
        aplicar_topes=True
    )
    
    if resultado["viable"]:
        print(f"✓ VIABLE")
    else:
        print(f"✗ NO VIABLE: {resultado['razon']}")
        if "sugerencia" in resultado:
            print(f"  💡 Sugerencia: {resultado['sugerencia']}")
    
    # Ejemplo 3: Mayoría calificada para MORENA (200-200 SIN topes) - debería funcionar
    print("\n\n3. Mayoría CALIFICADA para MORENA (200-200 SIN TOPES)")
    print("-"*100)
    resultado = calcular_mayoria_forzada(
        partido="MORENA",
        tipo_mayoria="calificada",
        mr_total=200,
        rp_total=200,
        aplicar_topes=False
    )
    
    if resultado["viable"]:
        print(f"✓ VIABLE")
        print(f"  Objetivo: {resultado['objetivo_escanos']} escaños")
        print(f"  MR ganados: {resultado['detalle']['mr_ganados']}/{resultado['detalle']['mr_total']} ({resultado['detalle']['pct_mr']}%)")
        print(f"  RP esperado: {resultado['detalle']['rp_esperado']}/{resultado['detalle']['rp_total']}")
        print(f"  Votos necesarios: {resultado['detalle']['pct_votos']}%")
        print(f"\n  Configuración para POST /procesar/diputados:")
        print(f"    mr_distritos_manuales: {resultado['mr_distritos_manuales']}")
        print(f"    votos_custom: {resultado['votos_custom']}")
        if resultado.get("advertencias"):
            print(f"\n  ⚠️  Advertencias:")
            for adv in resultado["advertencias"]:
                print(f"    - {adv}")
    else:
        print(f"✗ NO VIABLE: {resultado['razon']}")


if __name__ == "__main__":
    ejemplo_uso()
