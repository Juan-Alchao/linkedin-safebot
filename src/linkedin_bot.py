#!/usr/bin/env python3
"""
LinkedIn Automation Tool - Versión Práctica
Autor: Tu Nombre
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import json
import csv
from datetime import datetime
import logging
from pathlib import Path
import sys
import os

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

class Config:
    """Configuración de seguridad"""
    
    DAILY_LIMITS = {
        'connection_requests': 40,
        'messages': 20,
        'profile_visits': 150,
        'searches': 100
    }
    
    TIMING = {
        'min_action_delay': 2.5,
        'max_action_delay': 8.0,
        'break_every_actions': 10,
        'break_duration_min': 30,
        'break_duration_max': 180
    }
    
    SELECTORS = {
        'login_email': 'username',
        'login_password': 'password',
        'login_button': '//button[@type="submit"]',
        'connect_button': '//button[contains(@aria-label, "Invitar")]',
        'add_note_button': '//button[@aria-label="Añadir una nota"]',
        'message_textarea': '//textarea[@name="message"]',
        'send_button': '//button[@aria-label="Enviar ahora"]'
    }

# ============================================================================
# COMPORTAMIENTO HUMANO
# ============================================================================

class HumanBehavior:
    """Simulación de comportamiento humano"""
    
    @staticmethod
    def random_delay(min_seconds=2.5, max_seconds=8.0):
        """Retardo aleatorio con distribución normal"""
        mean = (min_seconds + max_seconds) / 2
        std_dev = (max_seconds - min_seconds) / 6
        delay = random.normalvariate(mean, std_dev)
        delay = max(min_seconds, min(max_seconds, delay))
        time.sleep(delay)
        return delay
    
    @staticmethod
    def human_typing(text, element):
        """Escribir texto como humano"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.03, 0.12))
    
    @staticmethod
    def take_break():
        """Tomar un descanso humano"""
        duration = random.uniform(30, 180)
        print(f"\n⏸️  Descanso: {duration:.1f} segundos")
        time.sleep(duration)

# ============================================================================
# AUTOMATIZACIÓN PRINCIPAL
# ============================================================================

class LinkedInAutomation:
    """Clase principal de automatización"""
    
    def __init__(self, email, password, account_name="default"):
        self.email = email
        self.password = password
        self.account_name = account_name
        self.driver = None
        self.behavior = HumanBehavior()
        
        # Configurar logging
        self._setup_logging()
        
        # Estadísticas
        self.daily_stats = self._load_daily_stats()
    
    def _setup_logging(self):
        """Configurar sistema de logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"{self.account_name}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_daily_stats(self):
        """Cargar estadísticas diarias"""
        stats_file = Path("logs") / f"{self.account_name}_daily.json"
        today = datetime.now().strftime('%Y-%m-%d')
        
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                data = json.load(f)
                if data.get('date') == today:
                    return data
        
        return {
            'date': today,
            'connections': 0,
            'messages': 0,
            'profiles': 0,
            'searches': 0
        }
    
    def _save_daily_stats(self):
        """Guardar estadísticas diarias"""
        stats_file = Path("logs") / f"{self.account_name}_daily.json"
        with open(stats_file, 'w') as f:
            json.dump(self.daily_stats, f, indent=2)
    
    def _check_daily_limits(self, action_type):
        """Verificar límites diarios"""
        limits = Config.DAILY_LIMITS
        
        if action_type == 'connection' and self.daily_stats['connections'] >= limits['connection_requests']:
            self.logger.warning(f"Límite diario alcanzado: {self.daily_stats['connections']}/{limits['connection_requests']}")
            return False
        elif action_type == 'message' and self.daily_stats['messages'] >= limits['messages']:
            self.logger.warning(f"Límite diario alcanzado: {self.daily_stats['messages']}/{limits['messages']}")
            return False
        
        return True
    
    def _update_daily_stats(self, action_type):
        """Actualizar estadísticas"""
        if action_type == 'connection':
            self.daily_stats['connections'] += 1
        elif action_type == 'message':
            self.daily_stats['messages'] += 1
        elif action_type == 'profile':
            self.daily_stats['profiles'] += 1
        elif action_type == 'search':
            self.daily_stats['searches'] += 1
        
        self._save_daily_stats()
    
    def setup_driver(self):
        """Configurar el navegador"""
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        
        # Perfil de usuario
        user_data_dir = Path("chrome_profiles") / self.account_name
        options.add_argument(f'--user-data-dir={user_data_dir.absolute()}')
        
        try:
            self.driver = uc.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
            self.logger.info("Navegador configurado exitosamente")
        except Exception as e:
            self.logger.error(f"Error configurando navegador: {e}")
            raise
    
    def login(self):
        """Iniciar sesión en LinkedIn"""
        try:
            self.logger.info("Iniciando sesión en LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            self.behavior.random_delay(3, 6)
            
            # Elementos de login
            email_field = self.driver.find_element(By.ID, Config.SELECTORS['login_email'])
            password_field = self.driver.find_element(By.ID, Config.SELECTORS['login_password'])
            login_button = self.driver.find_element(By.XPATH, Config.SELECTORS['login_button'])
            
            # Escribir credenciales
            self.behavior.human_typing(self.email, email_field)
            self.behavior.random_delay(1, 2)
            self.behavior.human_typing(self.password, password_field)
            self.behavior.random_delay(1, 3)
            
            # Login
            login_button.click()
            self.behavior.random_delay(5, 10)
            
            # Verificar
            if "feed" in self.driver.current_url:
                self.logger.info("✅ Login exitoso")
                return True
            else:
                self.logger.error("❌ Login fallido")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en login: {e}")
            return False
    
    def search_people(self, keywords, location="", limit=50):
        """Buscar personas en LinkedIn"""
        if not self._check_daily_limits('search'):
            return []
        
        try:
            self.logger.info(f"Buscando: {keywords} en {location if location else 'todo el mundo'}")
            
            # Construir URL
            search_url = "https://www.linkedin.com/search/results/people/"
            params = []
            
            if keywords:
                params.append(f"keywords={keywords.replace(' ', '%20')}")
            if location:
                params.append(f"location={location.replace(' ', '%20')}")
            
            if params:
                search_url += "?" + "&".join(params)
            
            self.driver.get(search_url)
            self.behavior.random_delay(4, 8)
            
            # Extraer perfiles
            profiles = []
            for _ in range(3):  # 3 páginas
                profile_elements = self.driver.find_elements(
                    By.XPATH, '//a[contains(@href, "/in/") and @tabindex="0"]'
                )
                
                for elem in profile_elements:
                    href = elem.get_attribute("href")
                    if href and "/in/" in href and href not in profiles:
                        profiles.append(href)
                
                if len(profiles) >= limit:
                    break
                
                # Siguiente página
                try:
                    next_button = self.driver.find_element(By.XPATH, '//button[@aria-label="Siguiente"]')
                    if next_button.is_enabled():
                        next_button.click()
                        self.behavior.random_delay(3, 6)
                except:
                    break
            
            self._update_daily_stats('search')
            self.logger.info(f"✅ Encontrados {len(profiles)} perfiles")
            return profiles[:limit]
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda: {e}")
            return []
    
    def send_connection_request(self, profile_url, message=None):
        """Enviar solicitud de conexión"""
        if not self._check_daily_limits('connection'):
            return {'status': 'limit_reached'}
        
        try:
            self.driver.get(profile_url)
            self.behavior.random_delay(4, 7)
            
            # Buscar botón de conectar
            connect_button = None
            try:
                connect_button = self.driver.find_element(By.XPATH, Config.SELECTORS['connect_button'])
            except:
                # Intentar otro selector
                connect_button = self.driver.find_element(By.XPATH, '//span[text()="Conectar"]/ancestor::button')
            
            if not connect_button:
                return {'status': 'no_button_found'}
            
            # Enviar conexión
            connect_button.click()
            self.behavior.random_delay(1, 2)
            
            # Añadir nota personalizada
            if message:
                try:
                    add_note_button = self.driver.find_element(By.XPATH, Config.SELECTORS['add_note_button'])
                    add_note_button.click()
                    self.behavior.random_delay(0.5, 1.5)
                    
                    textarea = self.driver.find_element(By.XPATH, Config.SELECTORS['message_textarea'])
                    self.behavior.human_typing(message, textarea)
                    self.behavior.random_delay(1, 2)
                except:
                    pass
            
            # Enviar
            send_button = self.driver.find_element(By.XPATH, Config.SELECTORS['send_button'])
            send_button.click()
            
            self.behavior.random_delay(2, 4)
            
            # Actualizar estadísticas
            self._update_daily_stats('connection')
            self.logger.info(f"✅ Conexión enviada a: {profile_url}")
            
            # Descanso
            self.behavior.random_delay(15, 45)
            
            return {'status': 'sent'}
            
        except Exception as e:
            self.logger.error(f"Error enviando conexión: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def run_safe_campaign(self, keywords, locations=None, connections_per_day=30):
        """Ejecutar campaña segura"""
        connections_sent = 0
        
        for keyword in keywords:
            if connections_sent >= connections_per_day:
                break
            
            for location in (locations or [""]):
                profiles = self.search_people(keyword, location, limit=20)
                
                for profile_url in profiles:
                    if connections_sent >= connections_per_day:
                        break
                    
                    result = self.send_connection_request(profile_url)
                    if result.get('status') == 'sent':
                        connections_sent += 1
                    
                    # Pausa entre perfiles
                    self.behavior.random_delay(5, 15)
        
        self.logger.info(f"🎯 Campaña completada: {connections_sent} conexiones")
        return {'connections_sent': connections_sent}
    
    def close(self):
        """Cerrar el navegador"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Navegador cerrado")

# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

def main():
    """Función principal"""
    
    print("\n" + "="*60)
    print("🚀 LINKEDIN AUTOMATION TOOL")
    print("="*60)
    
    # Configuración
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        print("\n🛠️  Configurando entorno...")
        
        # Crear directorios
        directories = ["logs", "chrome_profiles"]
        for dir_name in directories:
            Path(dir_name).mkdir(exist_ok=True)
            print(f"✅ Carpeta creada: {dir_name}/")
        
        print("\n🎉 Configuración completada")
        print("\nPasos siguientes:")
        print("1. Edita config.json.example y renómbralo a config.json")
        print("2. Añade tus credenciales de LinkedIn")
        print("3. Ejecuta: python src/linkedin_bot.py")
        return
    
    # Verificar configuración
    if not Path("config.json").exists():
        print("\n❌ Error: config.json no encontrado")
        print("Ejecuta primero: python src/linkedin_bot.py --setup")
        return
    
    # Cargar configuración
    with open("config.json", 'r') as f:
        config = json.load(f)
    
    # Inicializar bot
    account = config['accounts'][0]
    bot = LinkedInAutomation(account['email'], account['password'], account.get('name', 'default'))
    
    try:
        # Configurar y login
        print("\n⚙️  Configurando navegador...")
        bot.setup_driver()
        
        print("🔐 Iniciando sesión...")
        if not bot.login():
            print("❌ Error en login")
            return
        
        # Menú interactivo
        while True:
            print("\n" + "="*60)
            print("📋 MENÚ PRINCIPAL")
            print("="*60)
            print("1. 🔍 Buscar perfiles")
            print("2. 🤝 Enviar conexiones")
            print("3. 📊 Ver estadísticas")
            print("4. 🚪 Salir")
            print("="*60)
            
            choice = input("\nSelecciona (1-4): ").strip()
            
            if choice == "1":
                keyword = input("Palabras clave: ").strip()
                location = input("Ubicación: ").strip()
                limit = input("Límite (default 50): ").strip()
                limit = int(limit) if limit.isdigit() else 50
                
                print(f"\n🔍 Buscando: {keyword}...")
                profiles = bot.search_people(keyword, location, limit)
                print(f"✅ Encontrados: {len(profiles)} perfiles")
            
            elif choice == "2":
                keyword = input("Palabras clave: ").strip()
                max_conn = input("Máximo conexiones: ").strip()
                max_conn = int(max_conn) if max_conn.isdigit() else 10
                
                print(f"\n🤝 Enviando conexiones...")
                result = bot.run_safe_campaign([keyword], connections_per_day=max_conn)
                print(f"✅ Enviadas: {result['connections_sent']} conexiones")
            
            elif choice == "3":
                print("\n📊 ESTADÍSTICAS:")
                print(f"   Conexiones hoy: {bot.daily_stats['connections']}")
                print(f"   Mensajes hoy: {bot.daily_stats['messages']}")
                print(f"   Perfiles visitados: {bot.daily_stats['profiles']}")
                input("\nPresiona Enter para continuar...")
            
            elif choice == "4":
                print("\n👋 Saliendo...")
                break
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
  
