#!/usr/bin/env python3
"""
Script para instalar/actualizar ChromeDriver automáticamente
"""

import requests
import zipfile
import tarfile
import os
import sys
import stat
from pathlib import Path
import subprocess
import platform

BASE_DIR = Path(__file__).resolve().parent.parent

def get_chrome_version():
    """Obtener versión de Chrome instalada"""
    system = platform.system()
    
    try:
        if system == "Windows":
            # Windows
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                return version
            except:
                # Intentar ruta alternativa
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                return version
        
        elif system == "Darwin":  # macOS
            # Usar mdfind para encontrar Chrome
            result = subprocess.run(
                ["mdfind", "kMDItemCFBundleIdentifier == 'com.google.Chrome'"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                chrome_path = result.stdout.strip().split('\n')[0]
                plist_path = os.path.join(chrome_path, "Contents", "Info.plist")
                
                # Leer versión del plist
                result = subprocess.run(
                    ["defaults", "read", plist_path, "CFBundleShortVersionString"],
                    capture_output=True,
                    text=True
                )
                return result.stdout.strip()
        
        elif system == "Linux":
            # Linux - varios métodos
            methods = [
                ["google-chrome", "--version"],
                ["chromium", "--version"],
                ["chromium-browser", "--version"],
                ["google-chrome-stable", "--version"]
            ]
            
            for method in methods:
                try:
                    result = subprocess.run(method, capture_output=True, text=True)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        # Extraer número de versión
                        import re
                        match = re.search(r'\d+\.\d+\.\d+\.\d+', version)
                        if match:
                            return match.group()
                except:
                    continue
    
    except Exception as e:
        print(f"❌ Error obteniendo versión de Chrome: {e}")
    
    return None

def download_chromedriver(version):
    """Descargar ChromeDriver para la versión especificada"""
    
    if not version:
        print("❌ No se pudo detectar la versión de Chrome")
        return False
    
    # Extraer versión mayor
    major_version = version.split('.')[0]
    
    print(f"🔄 Versión de Chrome detectada: {version}")
    print(f"📦 Descargando ChromeDriver v{major_version}...")
    
    system = platform.system()
    architecture = platform.machine().lower()
    
    # Determinar URL según sistema operativo
    base_url = "https://chromedriver.storage.googleapis.com"
    
    # Obtener versión específica
    try:
        version_url = f"{base_url}/LATEST_RELEASE_{major_version}"
        response = requests.get(version_url)
        chromedriver_version = response.text.strip()
        print(f"✅ Versión de ChromeDriver: {chromedriver_version}")
    except:
        # Fallback a la versión general
        try:
            version_url = f"{base_url}/LATEST_RELEASE"
            response = requests.get(version_url)
            chromedriver_version = response.text.strip()
            print(f"⚠️  Usando versión general: {chromedriver_version}")
        except:
            print("❌ No se pudo obtener versión de ChromeDriver")
            return False
    
    # Determinar archivo a descargar
    if system == "Windows":
        filename = "chromedriver_win32.zip"
    elif system == "Darwin":
        if "arm" in architecture:
            filename = "chromedriver_mac_arm64.zip"
        else:
            filename = "chromedriver_mac64.zip"
    elif system == "Linux":
        filename = "chromedriver_linux64.zip"
    else:
        print(f"❌ Sistema operativo no soportado: {system}")
        return False
    
    download_url = f"{base_url}/{chromedriver_version}/{filename}"
    
    try:
        # Descargar
        print(f"📥 Descargando desde: {download_url}")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        # Guardar archivo
        download_path = BASE_DIR / "chromedriver.zip"
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("✅ Descarga completada")
        
        # Extraer
        print("📂 Extrayendo archivos...")
        
        if system == "Windows":
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(BASE_DIR)
        else:
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(BASE_DIR)
            
            # Hacer ejecutable en Unix
            chromedriver_path = BASE_DIR / "chromedriver"
            if chromedriver_path.exists():
                chromedriver_path.chmod(chromedriver_path.stat().st_mode | stat.S_IEXEC)
                print(f"✅ ChromeDriver hecho ejecutable: {chromedriver_path}")
        
        # Limpiar
        download_path.unlink()
        
        print("🎉 ChromeDriver instalado exitosamente")
        
        # Verificar instalación
        chromedriver_path = BASE_DIR / "chromedriver"
        if system == "Windows":
            chromedriver_path = BASE_DIR / "chromedriver.exe"
        
        if chromedriver_path.exists():
            print(f"📍 Ruta: {chromedriver_path.absolute()}")
            
            # Test simple
            try:
                result = subprocess.run(
                    [str(chromedriver_path), "--version"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"✅ Verificación: {result.stdout.strip()}")
                else:
                    print(f"⚠️  Verificación falló: {result.stderr}")
            except:
                print("⚠️  No se pudo verificar ChromeDriver")
            
            return True
        else:
            print("❌ ChromeDriver no encontrado después de extraer")
            return False
        
    except Exception as e:
        print(f"❌ Error instalando ChromeDriver: {e}")
        return False

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🛠️  INSTALADOR DE CHROMEDRIVER")
    print("="*60)
    
    print(f"\n📋 Sistema: {platform.system()} {platform.release()}")
    print(f"📋 Arquitectura: {platform.machine()}")
    print(f"📋 Python: {platform.python_version()}")
    
    # Verificar si ya existe
    chromedriver_name = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
    chromedriver_path = BASE_DIR / chromedriver_name
    
    if chromedriver_path.exists():
        print(f"\n⚠️  ChromeDriver ya existe en: {chromedriver_path}")
        
        try:
            result = subprocess.run(
                [str(chromedriver_path), "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"   Versión actual: {result.stdout.strip()}")
        except:
            pass
        
        overwrite = input("\n¿Reinstalar? (s/n): ").strip().lower()
        if overwrite != 's':
            print("❌ Cancelado")
            return
    
    # Obtener versión de Chrome
    version = get_chrome_version()
    
    if not version:
        print("\n❌ No se pudo detectar Chrome instalado")
        manual_version = input("Ingresa manualmente la versión mayor de Chrome (ej: 120): ").strip()
        if manual_version and manual_version.isdigit():
            version = f"{manual_version}.0.0.0"
        else:
            print("❌ Versión inválida")
            return
    
    # Descargar e instalar
    success = download_chromedriver(version)
    
    if success:
        print("\n" + "="*60)
        print("🎉 INSTALACIÓN COMPLETADA")
        print("="*60)
        print("\nPuedes ahora ejecutar el bot con:")
        print("  python src/linkedin_bot.py")
    else:
        print("\n❌ INSTALACIÓN FALLIDA")
        print("\nPuedes instalar ChromeDriver manualmente:")
        print("1. Ve a: https://chromedriver.chromium.org/")
        print("2. Descarga la versión que coincida con tu Chrome")
        print("3. Extrae chromedriver en la carpeta del proyecto")

if __name__ == "__main__":
    main()
