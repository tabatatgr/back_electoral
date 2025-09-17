mr_dip_robusto - Uso rápido

Archivo: `mr_dip_robusto.R`
Función: `mr_dip_robusto(df, siglado, EST='ID_ESTADO', DIST='ID_DISTRITO', FORM='partido_o_formula', VOTOS='votos_validos')`

Descripción:
- Normaliza clave compuesta ENT_CH (2 dígitos) y DIST_CH (3 dígitos) y crea DIST_UID = ENT_CH-DIST_CH.
- Filtra competidores basura (NULOS/NR/BLANCOS).
- Agrega votos por DIST_UID × FORM.
- Detecta ganadores por DIST_UID (con ties) y hace join con `siglado` usando la misma clave compuesta.
- Devuelve lista con `mr_siglado`, `ssd_tbl`, `faltantes` y `ties`.

Salida recomendada:
- Revisa `faltantes` para detectar problemas de mapeo fórmula->partido por territorio.
- Asegura `n_distinct(df_norm$DIST_UID) == 300` antes de pasar a `asignadip()`.

Ejemplo rápido:

```r
library(arrow)
source('mr_dip_robusto.R')
parq <- read_parquet('data/computos_diputados_2024.parquet')
sig <- read.csv('data/siglado-diputados-2024.csv', stringsAsFactors=FALSE)
res <- mr_dip_robusto(parq, sig, EST='ENTIDAD', DIST='DISTRITO', FORM='PARTIDO', VOTOS='VOTOS')
res$ssd_tbl
```

Notas:
- Ajusta los nombres de columnas a tus reales. La función advierte si no detecta 300 distritos.
- Si `faltantes` > 0, corrige el `siglado` para que tenga mapeo territorial de fórmula -> partido.
