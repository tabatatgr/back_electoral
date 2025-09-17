# mr_dip_robusto.R
# Función para calcular MR por distrito federal con chequeos robustos
library(dplyr)
library(stringr)

mr_dip_robusto <- function(df, siglado, EST = 'ID_ESTADO', DIST = 'ID_DISTRITO',
                           FORM = 'partido_o_formula', VOTOS = 'votos_validos') {
  df_norm <- df %>%
    mutate(
      ENT_CH  = str_pad(as.character(.data[[EST]]), width = 2, pad = '0'),
      DIST_CH = str_pad(as.character(.data[[DIST]]), width = 3, pad = '0'),
      DIST_UID = paste0(ENT_CH, '-', DIST_CH)
    ) %>%
    filter(!.data[[FORM]] %in% c('NULOS','NO REGISTRADO','NO REGISTRADOS','NR','BLANCOS',
                                 'VOTOS NULOS','CANDIDATO NO REGISTRADO', NA))

  # agregacion
  dist_comp <- df_norm %>%
    group_by(DIST_UID, .data[[FORM]]) %>%
    summarise(v = sum(.data[[VOTOS]], na.rm = TRUE), .groups = 'drop')

  # ganador por distrito (con ties)
  mr_ganador <- dist_comp %>%
    group_by(DIST_UID) %>%
    slice_max(order_by = v, n = 1, with_ties = TRUE) %>%
    mutate(tie = n() > 1) %>%
    ungroup()

  # normalizar siglado
  siglado_norm <- siglado %>%
    mutate(
      ENT_CH  = str_pad(as.character(.data[[EST]]), width = 2, pad = '0'),
      DIST_CH = str_pad(as.character(.data[[DIST]]), width = 3, pad = '0'),
      DIST_UID = paste0(ENT_CH, '-', DIST_CH)
    )

  # join
  # asumimos que siglado tiene columna con nombre identical a FORM indicando la formula o coalicion
  join_by <- c('DIST_UID', FORM)
  mr_siglado <- mr_ganador %>%
    left_join(siglado_norm, by = setNames(c('DIST_UID', FORM), c('DIST_UID', FORM)))

  # reportes
  faltantes <- mr_siglado %>% filter(is.na(partido_siglado) | is.na(coalicion))
  ties <- mr_siglado %>% filter(tie)

  ssd_tbl <- mr_siglado %>%
    filter(!tie) %>%
    group_by(partido_siglado) %>%
    summarise(ssd = n(), .groups = 'drop') %>%
    arrange(desc(ssd))

  # invariantes
  n_dist <- n_distinct(df_norm$DIST_UID)
  if (n_dist != 300) {
    warning(sprintf('Número de distritos detectado = %d (esperado 300). Revisa EST/DIST y padding.', n_dist))
  }
  if ((sum(!mr_siglado$tie) + sum(mr_siglado$tie)) != n_dist) {
    warning('Invariante de ganador por distrito rota: revisar duplicados o agrupaciones previas.')
  }

  list(df_norm = df_norm, dist_comp = dist_comp, mr_ganador = mr_ganador,
       mr_siglado = mr_siglado, faltantes = faltantes, ties = ties, ssd_tbl = ssd_tbl)
}

# fin mr_dip_robusto.R
