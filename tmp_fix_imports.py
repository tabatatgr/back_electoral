"""
Eliminar imports redundantes de math
"""
with open('tmp_generate_escenarios_con_topes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
first_import_math = True

for line in lines:
    # Mantener solo el primer "import math"
    if line.strip() == 'import math':
        if first_import_math:
            new_lines.append(line)
            first_import_math = False
        # else: skip redundant imports
    else:
        new_lines.append(line)

with open('tmp_generate_escenarios_con_topes.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✓ Archivo actualizado - eliminados imports redundantes de math")
