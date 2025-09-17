import pandas as pd
p='outputs/mr_audit_by_district.csv'
df = pd.read_csv(p, dtype=str).fillna('')
print('Total rows in audit:', len(df))
counts = df['mr_por_convenio'].str.upper().fillna('').value_counts()
print(counts.head(20).to_string())
print('\nRows with PRD as mr_por_convenio:')
print(df[df['mr_por_convenio'].str.upper()=='PRD'][['ENTIDAD','DISTRITO','postuladores','winner_by_votes_raw','winner_by_votes_valid','siglado_ppn','mr_por_convenio']].to_string(index=False))
