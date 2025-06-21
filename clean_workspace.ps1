# Script de limpieza automática para optimizar rendimiento de Cursor
# Ejecutar con: .\clean_workspace.ps1

Write-Host "🧹 Limpiando workspace para optimizar Cursor..." -ForegroundColor Green

# Limpiar archivos de caché Python
Write-Host "Eliminando archivos de caché Python..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Recurse -Include "__pycache__" -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path "." -Recurse -Include "*.pyc", "*.pyo", "*.pyd" | Remove-Item -Force -ErrorAction SilentlyContinue

# Limpiar archivos temporales
Write-Host "Eliminando archivos temporales..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Recurse -Include "*.tmp", "*.temp", "*~", "*.swp", "*.swo" | Remove-Item -Force -ErrorAction SilentlyContinue

# Limpiar archivos de backup
Write-Host "Eliminando archivos de backup..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Recurse -Include "*.bak", "*.backup", "*_backup", "*_old" | Remove-Item -Force -ErrorAction SilentlyContinue

# Limpiar caché de Streamlit
Write-Host "Eliminando caché de Streamlit..." -ForegroundColor Yellow
Remove-Item -Path ".streamlit\cache" -Recurse -Force -ErrorAction SilentlyContinue

# Limpiar logs
Write-Host "Eliminando logs..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Recurse -Include "*.log", "*.out" | Remove-Item -Force -ErrorAction SilentlyContinue

# Limpiar archivos de sistema
Write-Host "Eliminando archivos de sistema..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Recurse -Include ".DS_Store", "Thumbs.db", "*.db" | Remove-Item -Force -ErrorAction SilentlyContinue

# Limpiar checkpoints de Jupyter
Write-Host "Eliminando checkpoints de Jupyter..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Recurse -Include ".ipynb_checkpoints" -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✅ Limpieza completada! Cursor debería funcionar más rápido ahora." -ForegroundColor Green
Write-Host "💡 Ejecuta este script regularmente para mantener el rendimiento." -ForegroundColor Cyan 