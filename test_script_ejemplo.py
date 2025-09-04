#!/usr/bin/env python3
"""
Test del script de ejemplo para verificar métodos de reparto
"""

import sys
import os
sys.path.append('.')

# Copiar el script del usuario
from math import floor
from typing import Dict, List, Tuple, Optional

def _apply_threshold(votes: Dict[str, float], threshold: float) -> Dict[str, float]:
    total = sum(votes.values())
    if total <= 0:
        return {p: 0.0 for p in votes}
    kept = {}
    for p, v in votes.items():
        share = v / total if total else 0.0
        if share >= threshold:
            kept[p] = v
    return kept if kept else votes.copy()

def _normalize_dict(d: Dict[str, float]) -> Dict[str, float]:
    return {k: float(max(0.0, v)) for k, v in d.items()}

def _quota_value(total_votes: float, seats: int, method: str) -> float:
    method = method.lower()
    if seats <= 0:
        return float('inf')
    if method == "hare":
        return total_votes / seats
    elif method == "droop":
        return (total_votes / (seats + 1)) + 1e-12
    elif method == "imperiali":
        return total_votes / (seats + 2)
    else:
        raise ValueError(f"Unknown quota_method '{method}'. Use 'hare', 'droop', or 'imperiali'.")

def allocate_quota(votes: Dict[str, float], seats: int, quota_method: str = "hare", threshold: float = 0.0) -> Dict[str, int]:
    votes = _normalize_dict(votes)
    if seats <= 0 or sum(votes.values()) <= 0:
        return {p: 0 for p in votes}
    v = _apply_threshold(votes, threshold)
    parties = list(v.keys())
    if not parties:
        parties = list(votes.keys())
        v = votes.copy()
    total = sum(v.values())
    if total <= 0:
        return {p: 0 for p in votes}
    Q = _quota_value(total, seats, quota_method)
    base = {p: int((v[p] // Q)) for p in parties}
    allocated = sum(base.values())
    rems = {p: v[p] - base[p] * Q for p in parties}
    remaining = max(0, seats - allocated)
    order = sorted(parties, key=lambda p: (rems[p], v[p], p), reverse=True)
    for i in range(remaining):
        base[order[i % len(order)]] += 1
    out = {p: base.get(p, 0) for p in votes.keys()}
    return out

def _divisor_sequence(method: str, n: int):
    method = method.lower()
    if method in ("dhondt", "jefferson"):
        return [i for i in range(1, n + 1)]
    elif method in ("sainte_lague", "webster"):
        return [2*i - 1 for i in range(1, n + 1)]
    elif method in ("sainte_lague_mod", "webster_mod"):
        seq = [1.4]
        k = 3
        while len(seq) < n:
            seq.append(k); k += 2
        return seq
    else:
        raise ValueError("Unknown divisor_method. Use 'dhondt', 'sainte_lague', or 'sainte_lague_mod'.")

def allocate_divisor(votes: Dict[str, float], seats: int, divisor_method: str = "dhondt", threshold: float = 0.0) -> Dict[str, int]:
    votes = _normalize_dict(votes)
    if seats <= 0 or sum(votes.values()) <= 0:
        return {p: 0 for p in votes}
    v = _apply_threshold(votes, threshold)
    parties = list(v.keys())
    if not parties:
        parties = list(votes.keys())
        v = votes.copy()
    quotients = []
    divs = _divisor_sequence(divisor_method, seats * max(1, len(parties)))
    for p in parties:
        for d in divs:
            quotients.append((p, v[p] / d))
    quotients.sort(key=lambda x: (x[1], v[x[0]], x[0]), reverse=True)
    top = quotients[:seats]
    out = {p: 0 for p in votes.keys()}
    for p, _ in top:
        out[p] = out.get(p, 0) + 1
    return out

def test_script_ejemplo():
    """Test del script de ejemplo con datos reales"""
    
    print("🔍 TEST SCRIPT DE EJEMPLO")
    print("=" * 40)
    
    # Datos de ejemplo (simulando resultados electorales)
    votos = {
        "MORENA": 21741037,
        "PAN": 10165244,
        "PRI": 9112625,
        "PRD": 3163824,
        "PVEM": 2623767,
        "PT": 2595279,
        "MC": 258125,
        "PES": 626393,
        "NA": 89844
    }
    
    escanos_rp = 200  # Diputados RP
    umbral = 0.03
    
    print(f"📊 Votos totales: {sum(votos.values()):,}")
    print(f"🎯 Escaños a repartir: {escanos_rp}")
    print(f"🚪 Umbral: {umbral*100}%")
    print()
    
    print("1️⃣ MÉTODO CUOTA HARE + RESTOS MAYORES")
    resultado_hare = allocate_quota(votos, escanos_rp, quota_method="hare", threshold=umbral)
    total_hare = sum(resultado_hare.values())
    print(f"   ✅ Total asignado: {total_hare}")
    print(f"   📈 Resultados: {dict(sorted(resultado_hare.items(), key=lambda x: x[1], reverse=True))}")
    
    print()
    print("2️⃣ MÉTODO CUOTA DROOP + RESTOS MAYORES")
    resultado_droop = allocate_quota(votos, escanos_rp, quota_method="droop", threshold=umbral)
    total_droop = sum(resultado_droop.values())
    print(f"   ✅ Total asignado: {total_droop}")
    print(f"   📈 Resultados: {dict(sorted(resultado_droop.items(), key=lambda x: x[1], reverse=True))}")
    
    print()
    print("3️⃣ MÉTODO DIVISOR D'HONDT")
    resultado_dhondt = allocate_divisor(votos, escanos_rp, divisor_method="dhondt", threshold=umbral)
    total_dhondt = sum(resultado_dhondt.values())
    print(f"   ✅ Total asignado: {total_dhondt}")
    print(f"   📈 Resultados: {dict(sorted(resultado_dhondt.items(), key=lambda x: x[1], reverse=True))}")
    
    print()
    print("4️⃣ MÉTODO DIVISOR SAINTE-LAGUË")
    resultado_sl = allocate_divisor(votos, escanos_rp, divisor_method="sainte_lague", threshold=umbral)
    total_sl = sum(resultado_sl.values())
    print(f"   ✅ Total asignado: {total_sl}")
    print(f"   📈 Resultados: {dict(sorted(resultado_sl.items(), key=lambda x: x[1], reverse=True))}")
    
    print()
    print("🔄 COMPARACIÓN DE MÉTODOS:")
    print("   Partido | Hare | Droop | D'Hondt | S-Laguë")
    print("   --------|------|-------|---------|--------")
    
    for partido in sorted(votos.keys()):
        h = resultado_hare.get(partido, 0)
        d = resultado_droop.get(partido, 0)
        dh = resultado_dhondt.get(partido, 0)
        sl = resultado_sl.get(partido, 0)
        print(f"   {partido:7} | {h:4} | {d:5} | {dh:7} | {sl:7}")
    
    print()
    print("📋 VERIFICACIÓN DE ALGORITMOS:")
    
    # Verificar que todos asignan el total correcto
    if total_hare == escanos_rp:
        print("   ✅ Hare: Total correcto")
    else:
        print(f"   ❌ Hare: {total_hare} != {escanos_rp}")
        
    if total_droop == escanos_rp:
        print("   ✅ Droop: Total correcto")
    else:
        print(f"   ❌ Droop: {total_droop} != {escanos_rp}")
        
    if total_dhondt == escanos_rp:
        print("   ✅ D'Hondt: Total correcto")
    else:
        print(f"   ❌ D'Hondt: {total_dhondt} != {escanos_rp}")
        
    if total_sl == escanos_rp:
        print("   ✅ Sainte-Laguë: Total correcto")
    else:
        print(f"   ❌ Sainte-Laguë: {total_sl} != {escanos_rp}")

if __name__ == "__main__":
    test_script_ejemplo()
