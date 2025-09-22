param(
    [int]$Port = 8001
)

# Ruta a conda (ajustada al entorno detectado)
$conda = 'C:/Users/pablo/anaconda3/Scripts/conda.exe'
$envPath = 'c:\Users\pablo\OneDrive\Documentos\GitHub\back_electoral\.conda'

# Construir argumentos para conda run
$args = @('run', '-p', $envPath, '--no-capture-output', 'python', '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', $Port)

Write-Host "Launching uvicorn on http://127.0.0.1:$Port using conda environment at $envPath"

# Start-Process en modo detach (no ventana)
Start-Process -FilePath $conda -ArgumentList $args -WindowStyle Hidden

Write-Host "uvicorn start requested (detached). Check logs in terminal or use Get-Process to verify."
