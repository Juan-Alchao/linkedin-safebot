#!/usr/bin/env python3
"""
Instalador automático de ChromeDriver
"""

import os
import sys
import zipfile
import platform
import subprocess
import requests
from pathlib import Path

def main():
    print("\n🛠️  Instalando ChromeDriver...")
    
    # Determinar sistema operativo
    system = platform.system()
    
    if system == "Windows":
        filename = "chromedriver_win32.zip"
    elif system == "Darwin":
        filename = "chromedriver_mac64.zip"
    elif system == "Linux":
        filename = "chromedriver_linux64.zip"
    else:
        print(f"❌ Sistema no soportado: {system}")
        return 1
    
    # URL de ChromeDriver estable
    url = f"https://chromedriver.storage.googleapis.com/120.0.6099.109/{filename}"
    
    try:
        # Descargar
        print(f"📥 Descargando desde: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Guardar archivo
        script_dir = Path(__file__).parent.parent
        zip_path = script_dir / filename
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extraer
        print("📦 Extrayendo...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(script_dir)
        
        # Limpiar
        os.remove(zip_path)
        
        # Encontrar chromedriver
        for file in script_dir.iterdir():
            if "chromedriver" in file.name.lower() and not file.name.endswith('.py'):
                if system != "Windows":
                    os.chmod(file, 0o755)
                print(f"✅ ChromeDriver instalado en: {file}")
                break
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
  
