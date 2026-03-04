# Explicación: MORENA Recibe 29 Mejores Perdedores (No 0)

## Pregunta del Usuario

> "¿Por qué MORENA recibe 0 de mejor perdedor en el escenario hipotético?"

## Respuesta Directa

**MORENA NO recibe 0, recibe 29 escaños de mejores perdedores (PM)** ✅

## Evidencia de la Simulación

### Resultado MORENA 2024

Ejecutando `simular_escenario_300mr_100pm_100rp_por_partido.py`:

```
MORENA 2024:
MR  = 250 escaños (mayoría relativa)
PM  = 29 escaños  (mejores perdedores) ← SÍ recibe!
RP  = 42 escaños  (representación proporcional)
────────────────────────────────────────
Total = 321 escaños (64.2%)
```

### Archivo CSV Generado

```csv
Año,Coalición,Partido,MR_Escaños,PM_Escaños,RP_Escaños,Total_Escaños,Porcentaje
2024,SHH,MORENA,250,29,42,321,64.2
                    ^^
                    29 PM escaños
```

**Verificación:** 250 + 29 + 42 = 321 ✅

## ¿Por Qué Solo 29 PM (y no 100)?

### La Restricción

**MORENA ganó demasiados distritos en MR:**
- Ganó: 250 distritos MR (83.3%)
- Perdió: 50 distritos (16.7%)
- De esos 50 perdidos, MORENA quedó en 2º lugar en: **29**

### La Regla

**Solo puedes recibir PM de distritos que PERDISTE**
- Ganaste 250 → No puedes recibir PM de esos 250
- Perdiste 50 → Solo puedes recibir PM de esos 50
- Quedaste 2º en 29 → **Máximo PM posible: 29** ✅

## Tabla Comparativa

| Escenario | MR Ganados | Distritos Perdidos | 2dos Lugares | PM Máximo |
|-----------|------------|--------------------|--------------|-----------||
| Óptimo | 200 | 100 | ~100 | 100 |
| MORENA 2024 | **250** | **50** | **29** | **29** ✅ |
| Dominio total | 300 | 0 | 0 | 0 |

**Conclusión:** MORENA ganó tantos distritos MR que se quedó con pocos "perdidos" para recibir PM.

## ¿Quién Recibe Más PM?

### Comparación de Partidos 2024

| Partido | MR Ganados | Distritos Perdidos | PM Recibidos |
|---------|------------|--------------------|--------------||
| **PAN** | 36 | 264 | **38** ← Más PM |
| **MORENA** | 250 | 50 | **29** |
| **MC** | 1 | 299 | **18** |
| **PRI** | 7 | 293 | **14** |

**¿Por qué PAN recibe más PM que MORENA?**
- PAN ganó solo 36 MR → Perdió 264 distritos
- Muchas oportunidades de quedar en 2º lugar
- MORENA ganó 250 MR → Perdió solo 50 distritos
- Pocas oportunidades de quedar en 2º

## Desglose Completo 2024

### Sistema Hipotético (300 MR + 100 PM + 100 RP = 500 total)

| Partido | MR | PM | RP | Total | % |
|---------|----|----|-----|-------|-----|
| **MORENA** | **250** | **29** | **42** | **321** | **64.2%** |
| PVEM | 6 | 1 | 9 | 16 | 3.2% |
| PT | 0 | 0 | 6 | 6 | 1.2% |
| PAN | 36 | 38 | 18 | 92 | 18.4% |
| PRI | 7 | 14 | 12 | 33 | 6.6% |
| PRD | 0 | 0 | 2 | 2 | 0.4% |
| MC | 1 | 18 | 11 | 30 | 6.0% |
| **TOTAL** | **300** | **100** | **100** | **500** | **100%** |

## Validación

✅ Simulación ejecutada correctamente  
✅ MORENA recibe **29 PM** (no 0)  
✅ CSV generado como evidencia  
✅ Matemática verificada (250+29+42=321)  
✅ Lógica de exclusión funcionando  
✅ Todos los 100 PM distribuidos  

## Posible Fuente de Confusión

El usuario pudo haber visto:
1. **Sistema real mexicano**: No tiene componente separado de "MP" → Ahí sí sería 0
2. **Coalición vs Individual**: SHH coalition tiene 30 PM total, MORENA individual tiene 29
3. **Año diferente**: En 2021 MORENA tiene 34 PM

Pero **en el escenario hipotético de 2024**, MORENA SÍ recibe 29 mejores perdedores.

## Conclusión

**MORENA SÍ recibe mejores perdedores en el escenario hipotético:**
- 29 escaños PM (no 0)
- Limitado por haber ganado demasiados MR (250/300)
- Solo 50 distritos perdidos → Solo 29 segundos lugares
- Esto es correcto, no es un error

**No hay bug.** El sistema funciona como debe.

**La suposición del usuario de "0 MP" es incorrecta.** La evidencia muestra claramente 29 PM.
