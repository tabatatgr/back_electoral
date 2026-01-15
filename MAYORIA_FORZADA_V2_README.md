# Mayoría Forzada - Versión Realista

## ✅ Actualización Completada

Se actualizó el cálculo de mayoría forzada para usar **método REALISTA** basado en:
- `redistritacion/calcular_votos_minimos_morena.py`
- `redistritacion/generar_tabla_distritos_estados.py`

## 🎯 Método Realista

### Características:
1. **Redistritación Geográfica Real**
   - Usa método Hare de distribución de distritos por población
   - Considera pisos constitucionales (mínimo 2 distritos/estado)
   - Basado en datos reales del INE

2. **Votación Histórica 2024**
   - Usa votación real de MORENA por estado (42.49% nacional)
   - Escala proporcionalmente para alcanzar objetivo
   - Aplica factor de eficiencia geográfica +10% (realista)

3. **Distribución MR por Estado**
   - No asume proporcionalidad directa votos→MR
   - Calcula distrito por distrito considerando:
     * Votación histórica del estado
     * Distritos asignados por población
     * Factor de concentración geográfica

### Resultados Comparativos:

#### Mayoría Simple (201 escaños, 300 MR + 100 RP, CON TOPES):
| Método | MR Ganados | % Votos | Realismo |
|--------|-----------|---------|----------|
| Simplificado | 195 | 42% | ❌ Muy optimista |
| **Realista** | **145** | **47%** | ✅ Basado en datos reales |

#### Mayoría Calificada (267 escaños, 200 MR + 200 RP, SIN TOPES):
| Método | MR Ganados | % Votos | Realismo |
|--------|-----------|---------|----------|
| Simplificado | 180 (90%) | 45% | ❌ Imposible dominio |
| **Realista** | **133 (66.5%)** | **64%** | ✅ Difícil pero históricamente posible |

## 📊 Resultados de Tests

```
✓ TEST 1 PASADO: Mayoría simple MORENA (145 MR, 47% votos)
✓ TEST 2 PASADO: Mayoría calificada CON topes (correctamente rechazado)
✓ TEST 3 PASADO: Mayoría calificada SIN topes (133 MR, 64% votos)
✓ TEST 4 PASADO: Otros partidos

Total: 4/4 tests pasados 🎉
```

## 🔧 Archivos Modificados

1. **engine/calcular_mayoria_forzada_v2.py** (NUEVO)
   - Implementa método realista
   - Usa redistritación geográfica
   - Basado en votación histórica 2024
   - Fallback a método simplificado si no hay módulos

2. **main.py**
   - Actualizado para usar `calcular_mayoria_forzada_v2`
   - Endpoint GET `/calcular/mayoria_forzada` ahora usa método realista

3. **test_mayoria_forzada.py**
   - Actualizado para importar versión v2
   - Todos los tests pasan

## 📝 Conclusiones Clave

### Mayoría Simple (201 escaños):
- **Con topes (300-100)**: Requiere **47% votos** → 145 MR + 47 RP
- Alcanzable pero requiere votación fuerte
- Más realista que el 42% simplificado

### Mayoría Calificada (267 escaños):
- **Con topes**: IMPOSIBLE (requeriría 58.8% - nunca alcanzado en México)
- **Sin topes (200-200)**: Requiere **64% votos** → 133 MR + 128 RP
- Históricamente difícil pero no imposible
- MORENA 2024 obtuvo ~60% con coalición

### Ventajas del Método Realista:
1. ✅ Considera geografía real de México
2. ✅ Usa datos históricos verificables
3. ✅ Resultados más creíbles y alcanzables
4. ✅ No asume proporcionalidad directa
5. ✅ Incluye factor de eficiencia geográfica (+10%)

## 🚀 Uso en Frontend

```javascript
// Mayoría simple - MORENA (300-100 con topes)
GET /calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true

// Respuesta:
{
  "viable": true,
  "objetivo_escanos": 201,
  "mr_distritos_manuales": {"MORENA": 145, "PAN": 56, "PRI": 43, ...},
  "votos_custom": {"MORENA": 47.0, "PAN": 18.81, ...},
  "detalle": {
    "mr_ganados": 145,
    "pct_mr": 48.3,
    "rp_esperado": 47,
    "pct_votos": 47.0
  },
  "metodo": "Redistritación geográfica realista (Hare + eficiencia 1.1)"
}
```

## 💡 Próximos Pasos

1. ✅ Tests unitarios pasando (4/4)
2. ⏳ Test de integración con servidor
3. ⏳ Documentar endpoint en README
4. ⏳ Implementar botón en frontend

## 📚 Referencias

- `redistritacion/calcular_votos_minimos_morena.py` - Análisis de votos mínimos
- `redistritacion/generar_tabla_distritos_estados.py` - Distribución geográfica
- `redistritacion/outputs/distritos_morena_300_100 SIN TOPES.csv` - Datos reales
- Votación MORENA 2024: 42.49% (individual), ~60% (coalición)
