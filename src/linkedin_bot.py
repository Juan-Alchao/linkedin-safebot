"""
LinkedIn Automation Tool - Versión Práctica y Segura
Autor: [Tu Nombre]
GitHub: [Tu Repo]
Descripción: Herramienta para automatizar acciones en LinkedIn de forma segura y efectiva
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    ElementClickInterceptedException, StaleElementReferenceException
)
import time
import random
import json
import csv
from datetime import datetime, timedelta
import logging
from typing import Optional, List, Dict, Tuple
import sys
import os
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN DE PATHS
# ============================================================================

# Obtener directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Directorios para datos
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
EXPORTS_DIR = BASE_DIR / "exports"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
CHROME_PROFILES_DIR = BASE_DIR / "chrome_profiles"

# Crear directorios si no existen
for directory in [DATA_DIR, LOGS_DIR, EXPORTS_DIR, SCREENSHOTS_DIR, CHROME_PROFILES_DIR]:
    directory.mkdir(exist_ok=True)

# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================================

class Config:
    """Configuración práctica y segura para LinkedIn Automation"""
    
    # LÍMITES DIARIOS SEGUROS (por debajo de los límites oficiales de LinkedIn)
    DAILY_LIMITS = {
        'connection_requests': 40,      # LinkedIn permite ~100
        'messages': 20,                 # LinkedIn permite ~50
        'profile_visits': 150,          # LinkedIn permite ~300
        'withdrawals': 5,               # Retirar invitaciones pendientes
        'searches': 100                 # Búsquedas realizadas
    }
    
    # CONFIGURACIÓN DE TIEMPOS (en segundos)
    TIMING = {
        'min_action_delay': 2.5,        # Mínimo tiempo entre acciones
        'max_action_delay': 8.0,        # Máximo tiempo entre acciones
        'min_navigation_delay': 1.5,    # Mínimo tiempo en navegación
        'max_navigation_delay': 4.0,    # Máximo tiempo en navegación
        'break_every_actions': 10,      # Descanso cada X acciones
        'break_duration_min': 30,       # Duración mínima de descanso
        'break_duration_max': 180       # Duración máxima de descanso
    }
    
    # COMPORTAMIENTO HUMANO
    BEHAVIOR = {
        'scroll_variation': True,       # Variar el scroll
        'mouse_movements': True,        # Mover mouse ocasionalmente
        'typing_variation': True,       # Variar velocidad de escritura
        'error_rate': 0.05,             # 5% de errores simulados
        'random_breaks': True           # Pausas aleatorias
    }
    
    # SELECTORES DE LINKEDIN (actualizados)
    SELECTORS = {
        # Login
        'login_email': 'username',
        'login_password': 'password',
        'login_button': '//button[@type="submit"]',
        
        # Búsqueda
        'search_box': '//input[@aria-label="Buscar"]',
        'people_filter': '//button[contains(@aria-label, "Personas")]',
        
        # Conexiones
        'connect_button': '//button[contains(@aria-label, "Invitar")]',
        'connect_button_text': '//span[text()="Conectar"]/ancestor::button',
        'add_note_button': '//button[@aria-label="Añadir una nota"]',
        'message_textarea': '//textarea[@name="message"]',
        'send_button': '//button[@aria-label="Enviar ahora"]',
        
        # Mensajes
        'message_button': '//button[contains(@aria-label, "Enviar mensaje")]',
        'message_input': '//div[@role="textbox"]',
        'message_send': '//button[@type="submit"]',
        
        # Perfiles
        'profile_name': '//h1[contains(@class, "text-heading")]',
        'profile_title': '//div[contains(@class, "text-body-medium")]',
        
        # Navegación
        'next_page': '//button[@aria-label="Siguiente"]',
        'see_more_results': '//button[contains(@class, "artdeco-button--tertiary")]'
    }

# ============================================================================
# SISTEMA DE LOGGING MEJORADO
# ============================================================================

class Logger:
    """Sistema de logging avanzado para seguimiento de actividades"""
    
    def __init__(self, account_name: str = "default"):
        self.account_name = account_name
        
        # Configurar logger principal
        self.logger = logging.getLogger(f"linkedin_{account_name}")
        self.logger.setLevel(logging.INFO)
        
        # Formato personalizado
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo
        log_file = LOGS_DIR / f"{account_name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Archivo CSV para estadísticas detalladas
        self.stats_file = LOGS_DIR / f"{account_name}_stats.csv"
        self._init_stats_file()
        
        self.logger.info(f"Inicializado logger para cuenta: {account_name}")
    
    def _init_stats_file(self):
        """Inicializar archivo CSV de estadísticas"""
        if not self.stats_file.exists():
            with open(self.stats_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'action', 'target', 'result',
                    'daily_connections', 'daily_messages', 'notes'
                ])
    
    def info(self, message: str):
        """Registrar mensaje informativo"""
        self.logger.info(message)
        print(f"[INFO] {message}")
    
    def warning(self, message: str):
        """Registrar advertencia"""
        self.logger.warning(message)
        print(f"[WARNING] {message}")
    
    def error(self, message: str):
        """Registrar error"""
        self.logger.error(message)
        print(f"[ERROR] {message}")
    
    def success(self, message: str):
        """Registrar éxito"""
        self.logger.info(f"✅ {message}")
        print(f"✅ {message}")
    
    def log_action(self, action: str, target: str = "", result: str = "", 
                   daily_stats: Dict = None, notes: str = ""):
        """Registrar acción específica con estadísticas"""
        
        row = [
            datetime.now().isoformat(),
            action,
            target,
            result,
            daily_stats.get('connections', 0) if daily_stats else 0,
            daily_stats.get('messages', 0) if daily_stats else 0,
            notes
        ]
        
        with open(self.stats_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        self.logger.info(f"Acción: {action} -> {target} | Resultado: {result}")

# ============================================================================
# SIMULACIÓN DE COMPORTAMIENTO HUMANO
# ============================================================================

class HumanBehavior:
    """Clase para simular comportamiento humano realista"""
    
    @staticmethod
    def random_delay(min_seconds: float = None, max_seconds: float = None) -> float:
        """
        Retardo aleatorio con distribución normal (más realista)
        
        Args:
            min_seconds: Tiempo mínimo en segundos
            max_seconds: Tiempo máximo en segundos
        
        Returns:
            float: Tiempo de delay ejecutado
        """
        
        if min_seconds is None:
            min_seconds = Config.TIMING['min_action_delay']
        if max_seconds is None:
            max_seconds = Config.TIMING['max_action_delay']
        
        # Distribución normal centrada en el promedio
        mean = (min_seconds + max_seconds) / 2
        std_dev = (max_seconds - min_seconds) / 6  # 99.7% dentro del rango
        
        delay = random.normalvariate(mean, std_dev)
        
        # Asegurar que esté dentro del rango
        delay = max(min_seconds, min(max_seconds, delay))
        
        # Añadir micro-pausas durante el delay (como humano)
        steps = int(delay * 4)  # 4 pasos por segundo
        for i in range(steps):
            time.sleep(delay / steps)
            # Ocasionalmente añadir micro-variaciones
            if random.random() < 0.1:
                time.sleep(0.01 * random.random())
        
        return delay
    
    @staticmethod
    def human_typing(text: str, element) -> None:
        """
        Escribir texto como lo haría un humano
        
        Args:
            text: Texto a escribir
            element: Elemento Selenium donde escribir
        """
        
        for char in text:
            element.send_keys(char)
            
            # Variar velocidad de escritura
            if char in " .,!?":  # Pausas más largas después de puntuación
                time.sleep(random.uniform(0.05, 0.15))
            elif random.random() < 0.1:  # 10% de probabilidad de error de escritura
                # Simular error y corrección
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys(char)
            
            # Tiempo entre caracteres
            time.sleep(random.uniform(0.03, 0.12))
    
    @staticmethod
    def take_break(duration: float = None) -> None:
        """
        Tomar un descanso humano
        
        Args:
            duration: Duración específica del descanso (opcional)
        """
        
        if duration is None:
            duration = random.uniform(
                Config.TIMING['break_duration_min'],
                Config.TIMING['break_duration_max']
            )
        
        print(f"\n⏸️  Descanso humano: {duration:.1f} segundos...")
        
        # Dividir el descanso en segmentos (como humano revisando el teléfono)
        segments = int(duration / 10) if duration > 10 else 1
        for i in range(segments):
            segment_duration = duration / segments
            time.sleep(segment_duration)
            
            if segments > 1 and i < segments - 1:
                # Pequeña actividad durante el descanso
                if random.random() < 0.3:
                    print(f"   ...{int((i + 1) * segment_duration)} segundos de descanso")
    
    @staticmethod
    def simulate_scroll(driver, scroll_amount: int = None):
        """
        Simular scroll humano
        
        Args:
            driver: Instancia del driver de Selenium
            scroll_amount: Cantidad específica de scroll (opcional)
        """
        
        if not Config.BEHAVIOR['scroll_variation']:
            return
        
        try:
            if scroll_amount is None:
                scroll_amount = random.randint(100, 500)
            
            # Scroll suave con duración variable
            scroll_duration = random.uniform(0.3, 1.5)
            
            driver.execute_script(f"""
                window.scrollBy({{
                    top: {scroll_amount},
                    behavior: 'smooth'
                }});
            """)
            
            # Pequeña pausa después del scroll
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            # Silenciar errores de scroll
            pass
    
    @staticmethod
    def simulate_mouse_movement(driver):
        """
        Simular movimiento de mouse humano
        
        Args:
            driver: Instancia del driver de Selenium
        """
        
        if not Config.BEHAVIOR['mouse_movements']:
            return
        
        if random.random() < 0.3:  # 30% de probabilidad
            try:
                # Mover mouse a posición aleatoria
                x = random.randint(0, 1000)
                y = random.randint(0, 700)
                
                driver.execute_script(f"""
                    var evt = new MouseEvent('mousemove', {{
                        clientX: {x},
                        clientY: {y},
                        bubbles: true
                    }});
                    document.dispatchEvent(evt);
                """)
                
                time.sleep(0.1)
                
            except Exception as e:
                # Silenciar errores de mouse
                pass

# ============================================================================
# CLASE PRINCIPAL DE AUTOMATIZACIÓN
# ============================================================================

class LinkedInBot:
    """
    Clase principal para automatización de LinkedIn
    
    Esta clase maneja todas las interacciones con LinkedIn de forma segura
    y con comportamiento humano simulado.
    """
    
    def __init__(self, email: str, password: str, account_name: str = "default"):
        """
        Inicializar bot de LinkedIn
        
        Args:
            email: Email de la cuenta de LinkedIn
            password: Contraseña de la cuenta
            account_name: Nombre identificador para la cuenta
        """
        
        self.email = email
        self.password = password
        self.account_name = account_name
        
        # Componentes principales
        self.driver = None
        self.wait = None
        self.logger = Logger(account_name)
        self.behavior = HumanBehavior()
        
        # Estadísticas de sesión
        self.stats = {
            'connections_sent': 0,
            'messages_sent': 0,
            'profiles_visited': 0,
            'searches_done': 0,
            'start_time': datetime.now(),
            'last_action_time': datetime.now(),
            'action_count': 0
        }
        
        # Estadísticas diarias
        self.daily_stats = self._load_daily_stats()
        
        self.logger.info(f"Bot inicializado para: {email}")
    
    def _load_daily_stats(self) -> Dict:
        """
        Cargar estadísticas del día actual desde archivo
        
        Returns:
            Dict: Estadísticas diarias
        """
        
        stats_file = LOGS_DIR / f"{self.account_name}_daily.json"
        today = datetime.now().strftime('%Y-%m-%d')
        
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    data = json.load(f)
                    if data.get('date') == today:
                        self.logger.info(f"Estadísticas diarias cargadas: {data}")
                        return data
            except Exception as e:
                self.logger.error(f"Error cargando estadísticas: {e}")
        
        # Nuevo día - inicializar estadísticas
        return {
            'date': today,
            'connections': 0,
            'messages': 0,
            'profiles': 0,
            'searches': 0,
            'withdrawals': 0
        }
    
    def _save_daily_stats(self):
        """Guardar estadísticas diarias en archivo"""
        
        stats_file = LOGS_DIR / f"{self.account_name}_daily.json"
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.daily_stats, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error guardando estadísticas: {e}")
    
    def _check_daily_limits(self, action_type: str) -> bool:
        """
        Verificar si se ha alcanzado el límite diario para una acción
        
        Args:
            action_type: Tipo de acción ('connection', 'message', 'profile', 'search')
        
        Returns:
            bool: True si se puede realizar la acción, False si se alcanzó el límite
        """
        
        limits = Config.DAILY_LIMITS
        
        if action_type == 'connection':
            if self.daily_stats['connections'] >= limits['connection_requests']:
                self.logger.warning(
                    f"Límite diario de conexiones alcanzado: "
                    f"{self.daily_stats['connections']}/{limits['connection_requests']}"
                )
                return False
        
        elif action_type == 'message':
            if self.daily_stats['messages'] >= limits['messages']:
                self.logger.warning(
                    f"Límite diario de mensajes alcanzado: "
                    f"{self.daily_stats['messages']}/{limits['messages']}"
                )
                return False
        
        elif action_type == 'profile':
            if self.daily_stats['profiles'] >= limits['profile_visits']:
                self.logger.warning(
                    f"Límite diario de perfiles visitados alcanzado: "
                    f"{self.daily_stats['profiles']}/{limits['profile_visits']}"
                )
                return False
        
        elif action_type == 'search':
            if self.daily_stats['searches'] >= limits['searches']:
                self.logger.warning(
                    f"Límite diario de búsquedas alcanzado: "
                    f"{self.daily_stats['searches']}/{limits['searches']}"
                )
                return False
        
        return True
    
    def _update_daily_stats(self, action_type: str):
        """
        Actualizar estadísticas diarias
        
        Args:
            action_type: Tipo de acción realizada
        """
        
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
        """Configurar el navegador Chrome para evitar detección"""
        
        try:
            options = uc.ChromeOptions()
            
            # Configuraciones para evitar detección
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            
            # Perfil de usuario persistente
            profile_dir = CHROME_PROFILES_DIR / self.account_name
            profile_dir.mkdir(exist_ok=True)
            options.add_argument(f'--user-data-dir={profile_dir.absolute()}')
            
            # Configuraciones adicionales
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            
            # Eliminar indicadores de automatización
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Inicializar ChromeDriver indetectable
            self.driver = uc.Chrome(
                options=options,
                use_subprocess=True
            )
            
            # Eliminar propiedad webdriver del navegador
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
            )
            
            # Configurar timeout de espera
            self.wait = WebDriverWait(self.driver, 10)
            
            self.logger.success("Navegador configurado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error configurando el navegador: {e}")
            raise
    
    def login(self) -> bool:
        """
        Iniciar sesión en LinkedIn
        
        Returns:
            bool: True si el login fue exitoso, False en caso contrario
        """
        
        try:
            self.logger.info("Iniciando sesión en LinkedIn...")
            
            # Navegar a página de login
            self.driver.get("https://www.linkedin.com/login")
            self.behavior.random_delay(3, 6)
            
            # Esperar campos de login
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, Config.SELECTORS['login_email']))
            )
            
            password_field = self.driver.find_element(By.ID, Config.SELECTORS['login_password'])
            
            # Escribir email como humano
            self.behavior.human_typing(self.email, email_field)
            self.behavior.random_delay(1, 2)
            
            # Escribir contraseña como humano
            self.behavior.human_typing(self.password, password_field)
            self.behavior.random_delay(1, 3)
            
            # Hacer clic en botón de login
            login_button = self.driver.find_element(By.XPATH, Config.SELECTORS['login_button'])
            login_button.click()
            
            # Esperar a que el login se complete
            self.behavior.random_delay(5, 10)
            
            # Verificar si el login fue exitoso
            current_url = self.driver.current_url
            if "feed" in current_url or "in/" in current_url:
                self.logger.success("✅ Login exitoso")
                
                # Tomar screenshot como evidencia
                try:
                    screenshot_file = SCREENSHOTS_DIR / f"login_success_{datetime.now().strftime('%H%M%S')}.png"
                    self.driver.save_screenshot(str(screenshot_file))
                except:
                    pass
                
                return True
            
            # Verificar si hay CAPTCHA o verificación de seguridad
            elif "checkpoint" in current_url or "security" in current_url:
                self.logger.warning("⚠️  LinkedIn solicita verificación adicional")
                
                # Tomar screenshot para debug
                try:
                    screenshot_file = SCREENSHOTS_DIR / f"verification_needed_{datetime.now().strftime('%H%M%S')}.png"
                    self.driver.save_screenshot(str(screenshot_file))
                except:
                    pass
                
                # Pausar para verificación manual
                print("\n" + "="*60)
                print("⚠️  VERIFICACIÓN REQUERIDA")
                print("LinkedIn solicita verificación adicional.")
                print("Por favor, completa la verificación manualmente en el navegador.")
                print("El sistema esperará 60 segundos...")
                print("="*60 + "\n")
                
                time.sleep(60)
                
                # Verificar si ahora está logueado
                current_url = self.driver.current_url
                if "feed" in current_url or "in/" in current_url:
                    self.logger.success("✅ Verificación completada manualmente")
                    return True
            
            self.logger.error(f"❌ Login fallido - URL actual: {current_url}")
            return False
            
        except TimeoutException:
            self.logger.error("❌ Timeout en el login - LinkedIn no respondió")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error en login: {e}")
            
            # Tomar screenshot del error
            try:
                screenshot_file = SCREENSHOTS_DIR / f"login_error_{datetime.now().strftime('%H%M%S')}.png"
                self.driver.save_screenshot(str(screenshot_file))
            except:
                pass
            
            return False
    
    def search_people(self, keywords: str, location: str = "", limit: int = 50) -> List[str]:
        """
        Buscar personas en LinkedIn
        
        Args:
            keywords: Palabras clave para la búsqueda
            location: Ubicación para filtrar (opcional)
            limit: Límite máximo de perfiles a obtener
        
        Returns:
            List[str]: Lista de URLs de perfiles encontrados
        """
        
        if not self._check_daily_limits('search'):
            return []
        
        try:
            self.logger.info(f"🔍 Buscando personas: {keywords} en {location if location else 'todo el mundo'}")
            
            # Construir URL de búsqueda
            search_url = "https://www.linkedin.com/search/results/people/"
            params = []
            
            if keywords:
                params.append(f"keywords={keywords.replace(' ', '%20')}")
            if location:
                params.append(f"location={location.replace(' ', '%20')}")
            
            if params:
                search_url += "?" + "&".join(params)
            
            # Navegar a la búsqueda
            self.driver.get(search_url)
            self.behavior.random_delay(4, 8)
            
            # Intentar aplicar filtro "Personas" si es necesario
            try:
                people_filter = self.driver.find_element(By.XPATH, Config.SELECTORS['people_filter'])
                if "selected" not in people_filter.get_attribute("class"):
                    people_filter.click()
                    self.behavior.random_delay(2, 4)
            except:
                # El filtro ya está aplicado o no se encuentra
                pass
            
            profiles = []
            pages_to_scroll = 3  # Número de páginas a recorrer
            
            for page in range(pages_to_scroll):
                # Scroll para cargar más resultados
                self.behavior.simulate_scroll(self.driver)
                self.behavior.random_delay(2, 4)
                
                # Extraer enlaces de perfiles de la página actual
                profile_elements = self.driver.find_elements(
                    By.XPATH, '//a[contains(@href, "/in/") and @tabindex="0"]'
                )
                
                for elem in profile_elements:
                    href = elem.get_attribute("href")
                    if href and "/in/" in href and href not in profiles:
                        profiles.append(href)
                
                self.logger.info(f"Página {page + 1}: {len(profiles)} perfiles encontrados")
                
                # Verificar si alcanzamos el límite
                if len(profiles) >= limit:
                    break
                
                # Intentar ir a la siguiente página
                try:
                    next_button = self.driver.find_element(By.XPATH, Config.SELECTORS['next_page'])
                    if next_button.is_enabled():
                        next_button.click()
                        self.behavior.random_delay(3, 6)
                    else:
                        # No hay más páginas
                        break
                except:
                    # No se encontró botón de siguiente página
                    break
            
            # Actualizar estadísticas
            self._update_daily_stats('search')
            self.stats['searches_done'] += 1
            
            self.logger.success(f"✅ Búsqueda completada: {len(profiles)} perfiles encontrados")
            return profiles[:limit]
            
        except Exception as e:
            self.logger.error(f"❌ Error en búsqueda: {e}")
            return []
    
    def extract_profile_info(self, profile_url: str) -> Dict:
        """
        Extraer información básica de un perfil
        
        Args:
            profile_url: URL del perfil de LinkedIn
        
        Returns:
            Dict: Información extraída del perfil
        """
        
        try:
            self.driver.get(profile_url)
            self.behavior.random_delay(4, 7)
            
            # Simular lectura humana del perfil
            self.behavior.simulate_scroll(self.driver)
            self.behavior.simulate_mouse_movement(self.driver)
            self.behavior.random_delay(2, 5)
            
            info = {
                'url': profile_url,
                'name': '',
                'title': '',
                'location': '',
                'extracted_at': datetime.now().isoformat()
            }
            
            # Intentar extraer nombre
            try:
                name_element = self.driver.find_element(By.XPATH, Config.SELECTORS['profile_name'])
                info['name'] = name_element.text.strip()
            except NoSuchElementException:
                self.logger.warning(f"No se pudo extraer nombre de: {profile_url}")
            
            # Intentar extraer título profesional
            try:
                title_element = self.driver.find_element(By.XPATH, Config.SELECTORS['profile_title'])
                info['title'] = title_element.text.strip()
            except NoSuchElementException:
                self.logger.warning(f"No se pudo extraer título de: {profile_url}")
            
            # Intentar extraer ubicación (múltiples selectores posibles)
            try:
                location_selectors = [
                    '//span[contains(@class, "text-body-small")]',
                    '//div[contains(@class, "pv-text-details__left-panel")]//span[contains(@class, "text-body-small")]',
                    '//div[contains(@class, "pv-top-card")]//span[contains(@class, "text-body-small")]'
                ]
                
                for selector in location_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        for elem in elements:
                            text = elem.text.strip()
                            if text and len(text) < 100:  # Filtrar textos muy largos
                                info['location'] = text
                                break
                        if info['location']:
                            break
                    except:
                        continue
            except:
                pass
            
            # Actualizar estadísticas
            self.stats['profiles_visited'] += 1
            self._update_daily_stats('profile')
            
            return info
            
        except Exception as e:
            self.logger.error(f"❌ Error extrayendo información de {profile_url}: {e}")
            return {'url': profile_url, 'error': str(e)}
    
    def send_connection_request(self, profile_url: str, message: str = None) -> Dict:
        """
        Enviar solicitud de conexión a un perfil
        
        Args:
            profile_url: URL del perfil objetivo
            message: Mensaje personalizado (opcional)
        
        Returns:
            Dict: Resultado de la operación
        """
        
        if not self._check_daily_limits('connection'):
            return {
                'status': 'limit_reached', 
                'profile': profile_url,
                'timestamp': datetime.now().isoformat()
            }
        
        result = {
            'profile': profile_url,
            'status': 'unknown',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Visitar perfil primero para obtener información
            profile_info = self.extract_profile_info(profile_url)
            result['profile_info'] = profile_info
            
            self.behavior.random_delay(3, 6)
            
            # Buscar botón de conectar con múltiples estrategias
            connect_button = None
            
            # Lista de selectores posibles para el botón de conectar
            connect_selectors = [
                Config.SELECTORS['connect_button'],
                Config.SELECTORS['connect_button_text'],
                '//button[span[text()="Connect"]]',
                '//button[contains(@class, "pv-s-profile-actions")]//span[text()="Connect"]/..',
                '//button[contains(@aria-label, "Connect")]'
            ]
            
            for selector in connect_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            connect_button = btn
                            break
                    if connect_button:
                        break
                except:
                    continue
            
            if not connect_button:
                # Verificar si ya están conectados
                already_connected_selectors = [
                    '//span[text()="Enviar mensaje"]',
                    '//span[text()="Send message"]',
                    '//span[contains(text(), "Ya están conectados")]',
                    '//span[contains(text(), "Message")]'
                ]
                
                for selector in already_connected_selectors:
                    try:
                        if self.driver.find_element(By.XPATH, selector):
                            result['status'] = 'already_connected'
                            self.logger.info(f"✅ Ya conectado: {profile_url}")
                            return result
                    except:
                        continue
                
                result['status'] = 'no_button_found'
                self.logger.warning(f"⚠️  No se encontró botón de conectar: {profile_url}")
                return result
            
            # Hacer clic en el botón de conectar
            connect_button.click()
            self.behavior.random_delay(1, 2)
            
            # Verificar si aparece el modal para añadir nota
            note_added = False
            
            try:
                add_note_button = self.driver.find_element(
                    By.XPATH, Config.SELECTORS['add_note_button']
                )
                
                if add_note_button.is_displayed():
                    add_note_button.click()
                    self.behavior.random_delay(0.5, 1.5)
                    
                    # Generar o usar mensaje personalizado
                    if not message:
                        message = self._generate_connection_message(profile_info)
                    
                    # Escribir mensaje en el textarea
                    textarea = self.driver.find_element(
                        By.XPATH, Config.SELECTORS['message_textarea']
                    )
                    
                    self.behavior.human_typing(message, textarea)
                    self.behavior.random_delay(1, 2)
                    
                    note_added = True
                    result['message_sent'] = message
                    
            except Exception as e:
                # No se pudo añadir nota (modal no apareció o ya está conectado)
                self.logger.debug(f"No se pudo añadir nota: {e}")
            
            # Enviar la invitación
            try:
                send_button = self.driver.find_element(
                    By.XPATH, Config.SELECTORS['send_button']
                )
                send_button.click()
                
                self.behavior.random_delay(2, 4)
                
                result['status'] = 'sent'
                result['note_added'] = note_added
                
                # Actualizar estadísticas
                self.stats['connections_sent'] += 1
                self._update_daily_stats('connection')
                
                self.logger.success(
                    f"✅ Conexión enviada a: {profile_info.get('name', 'Unknown')} | "
                    f"Nota: {'Sí' if note_added else 'No'}"
                )
                
                # Registrar acción en log detallado
                self.logger.log_action(
                    action="connection_request",
                    target=profile_url,
                    result="sent",
                    daily_stats=self.daily_stats,
                    notes=f"Note: {note_added}, Name: {profile_info.get('name', 'Unknown')}"
                )
                
                # Descanso más largo después de enviar conexión
                self.behavior.random_delay(15, 45)
                
            except Exception as e:
                result['status'] = 'send_failed'
                result['error'] = str(e)
                self.logger.error(f"❌ Error enviando conexión: {e}")
            
            return result
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.logger.error(f"❌ Error en send_connection_request: {e}")
            return result
    
    def _generate_connection_message(self, profile_info: Dict) -> str:
        """
        Generar mensaje personalizado para solicitud de conexión
        
        Args:
            profile_info: Información del perfil
        
        Returns:
            str: Mensaje personalizado
        """
        
        name = profile_info.get('name', '').split()[0] if profile_info.get('name') else ''
        title = profile_info.get('title', '')
        
        # Plantillas de mensajes variadas
        templates_spanish = [
            f"Hola {name}, me encantaría conectar y ampliar nuestra red profesional. Saludos!",
            f"Hola {name}, vi tu perfil y me pareció interesante conectar. Saludos!",
            f"Hola {name}, busco expandir mi red profesional con personas del sector. ¿Te gustaría conectar?",
            f"Hola {name}, veo que trabajas en {title.split(' at ')[-1] if ' at ' in title else 'tu sector'}. Me gustaría conectar para intercambiar ideas.",
            f"Hola {name}, me gustaría añadirte a mi red profesional. Saludos cordiales!"
        ]
        
        templates_english = [
            f"Hi {name}, I'd like to connect and expand our professional network. Best regards!",
            f"Hello {name}, I came across your profile and found it interesting to connect. Best!",
            f"Hi {name}, I'm looking to expand my professional network in the industry. Would you like to connect?",
            f"Hello {name}, I see you work in {title.split(' at ')[-1] if ' at ' in title else 'your industry'}. I'd like to connect to exchange ideas.",
            f"Hi {name}, I'd like to add you to my professional network. Best regards!"
        ]
        
        # Combinar plantillas
        all_templates = templates_spanish + templates_english
        
        return random.choice(all_templates)
    
    def send_message(self, profile_url: str, message: str) -> Dict:
        """
        Enviar mensaje a una conexión
        
        Args:
            profile_url: URL del perfil
            message: Mensaje a enviar
        
        Returns:
            Dict: Resultado de la operación
        """
        
        if not self._check_daily_limits('message'):
            return {'status': 'limit_reached', 'profile': profile_url}
        
        result = {
            'profile': profile_url,
            'status': 'unknown',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Visitar perfil
            self.driver.get(profile_url)
            self.behavior.random_delay(3, 6)
            
            # Buscar botón de mensaje
            message_button = None
            
            message_selectors = [
                Config.SELECTORS['message_button'],
                '//button[span[text()="Enviar mensaje"]]',
                '//button[span[text()="Message"]]'
            ]
            
            for selector in message_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            message_button = btn
                            break
                    if message_button:
                        break
                except:
                    continue
            
            if not message_button:
                result['status'] = 'no_message_button'
                self.logger.warning(f"⚠️  No se encontró botón de mensaje: {profile_url}")
                return result
            
            # Hacer clic en mensaje
            message_button.click()
            self.behavior.random_delay(2, 4)
            
            # Escribir mensaje
            message_input = self.driver.find_element(
                By.XPATH, Config.SELECTORS['message_input']
            )
            
            self.behavior.human_typing(message, message_input)
            self.behavior.random_delay(1, 2)
            
            # Enviar mensaje
            send_button = self.driver.find_element(
                By.XPATH, Config.SELECTORS['message_send']
            )
            send_button.click()
            
            self.behavior.random_delay(2, 4)
            
            result['status'] = 'sent'
            
            # Actualizar estadísticas
            self.stats['messages_sent'] += 1
            self._update_daily_stats('message')
            
            self.logger.success(f"✅ Mensaje enviado a: {profile_url}")
            self.logger.log_action(
                "send_message",
                profile_url,
                "sent",
                self.daily_stats,
                f"Message length: {len(message)}"
            )
            
            # Descanso más largo después de enviar mensaje
            self.behavior.random_delay(30, 90)
            
            return result
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.logger.error(f"❌ Error enviando mensaje: {e}")
            return result
    
    def run_campaign(self, keywords: List[str], locations: List[str] = None,
                     connections_per_day: int = 30, messages_per_day: int = 15) -> Dict:
        """
        Ejecutar una campaña completa de conexiones
        
        Args:
            keywords: Lista de palabras clave para buscar
            locations: Lista de ubicaciones (opcional)
            connections_per_day: Número máximo de conexiones por día
            messages_per_day: Número máximo de mensajes por día
        
        Returns:
            Dict: Resultados de la campaña
        """
        
        self.logger.info(f"🚀 Iniciando campaña con keywords: {keywords}")
        
        # Establecer objetivos diarios (respetando límites de configuración)
        daily_goals = {
            'connections': min(connections_per_day, Config.DAILY_LIMITS['connection_requests']),
            'messages': min(messages_per_day, Config.DAILY_LIMITS['messages'])
        }
        
        self.logger.info(f"🎯 Objetivos diarios: {daily_goals}")
        
        connections_sent = 0
        messages_sent = 0
        
        for keyword in keywords:
            # Verificar si ya alcanzamos el objetivo de conexiones
            if connections_sent >= daily_goals['connections']:
                self.logger.success("✅ Objetivo de conexiones diarias alcanzado")
                break
            
            for location in (locations or [""]):
                # Buscar perfiles con esta keyword y ubicación
                profiles = self.search_people(keyword, location, limit=20)
                
                for profile_url in profiles:
                    # Verificar límite diario nuevamente
                    if connections_sent >= daily_goals['connections']:
                        break
                    
                    # Enviar solicitud de conexión
                    result = self.send_connection_request(profile_url)
                    
                    if result.get('status') == 'sent':
                        connections_sent += 1
                        
                        # Ocasionalmente enviar mensaje de seguimiento (10% de las veces)
                        if messages_sent < daily_goals['messages'] and random.random() < 0.1:
                            follow_up_message = "Gracias por aceptar mi invitación. ¡Espero que podamos mantener el contacto!"
                            message_result = self.send_message(profile_url, follow_up_message)
                            
                            if message_result.get('status') == 'sent':
                                messages_sent += 1
                    
                    # Control de pausas y descansos
                    self.stats['action_count'] += 1
                    
                    # Descanso cada X acciones
                    if self.stats['action_count'] % Config.TIMING['break_every_actions'] == 0:
                        self.behavior.take_break()
                        self.stats['action_count'] = 0
                    
                    # Pausa entre perfiles
                    self.behavior.random_delay(5, 15)
                
                # Pausa más larga entre ubicaciones
                if location and location != "":
                    self.behavior.random_delay(10, 30)
        
        # Resumen de la campaña
        self.logger.success(
            f"🎯 Campaña completada: {connections_sent} conexiones enviadas, "
            f"{messages_sent} mensajes enviados"
        )
        
        return {
            'connections_sent': connections_sent,
            'messages_sent': messages_sent,
            'profiles_visited': self.stats['profiles_visited'],
            'daily_stats': self.daily_stats,
            'campaign_completed': True
        }
    
    def save_profiles_to_csv(self, profiles: List[Dict], filename: str = None):
        """
        Guardar perfiles en archivo CSV
        
        Args:
            profiles: Lista de diccionarios con información de perfiles
            filename: Nombre del archivo (opcional)
        """
        
        if not profiles:
            self.logger.warning("No hay perfiles para guardar")
            return
        
        if not filename:
            filename = f"profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = DATA_DIR / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                # Usar todas las claves del primer perfil como columnas
                fieldnames = profiles[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(profiles)
            
            self.logger.success(f"✅ {len(profiles)} perfiles guardados en: {filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Error guardando perfiles: {e}")
    
    def export_session_data(self, export_type: str = "all"):
        """
        Exportar datos de la sesión
        
        Args:
            export_type: Tipo de exportación ('stats', 'logs', 'all')
        """
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_type in ["stats", "all"]:
            # Exportar estadísticas
            stats_data = {
                'session_stats': self.stats,
                'daily_stats': self.daily_stats,
                'export_time': datetime.now().isoformat()
            }
            
            stats_file = EXPORTS_DIR / f"session_stats_{timestamp}.json"
            with open(stats_file, 'w') as f:
                json.dump(stats_data, f, indent=2)
            
            self.logger.info(f"📊 Estadísticas exportadas: {stats_file}")
        
        if export_type in ["logs", "all"]:
            # Exportar logs recientes
            log_files = list(LOGS_DIR.glob(f"{self.account_name}*.log"))
            for log_file in log_files:
                export_log = EXPORTS_DIR / f"log_{timestamp}_{log_file.name}"
                try:
                    export_log.write_text(log_file.read_text())
                except:
                    pass
            
            self.logger.info(f"📝 Logs exportados")
    
    def close(self):
        """Cerrar sesión y limpiar recursos"""
        
        try:
            # Exportar datos de la sesión
            self.export_session_data("stats")
            
            # Cerrar navegador
            if self.driver:
                self.driver.quit()
                self.logger.info("🌐 Navegador cerrado")
        
        except Exception as e:
            self.logger.error(f"Error cerrando sesión: {e}")
        
        finally:
            # Guardar estadísticas finales de sesión
            session_stats_file = LOGS_DIR / f"{self.account_name}_session_final.json"
            
            final_stats = {
                'session_start': self.stats['start_time'].isoformat(),
                'session_end': datetime.now().isoformat(),
                'duration_minutes': round((datetime.now() - self.stats['start_time']).total_seconds() / 60, 2),
                'connections_sent': self.stats['connections_sent'],
                'messages_sent': self.stats['messages_sent'],
                'profiles_visited': self.stats['profiles_visited'],
                'searches_done': self.stats['searches_done'],
                'daily_stats': self.daily_stats,
                'summary': f"Conectado {self.stats['connections_sent']} personas en "
                          f"{round((datetime.now() - self.stats['start_time']).total_seconds() / 60, 1)} minutos"
            }
            
            try:
                with open(session_stats_file, 'w') as f:
                    json.dump(final_stats, f, indent=2)
            except:
                pass
            
            self.logger.info("="*60)
            self.logger.info("✅ SESIÓN FINALIZADA")
            self.logger.info("="*60)
            self.logger.info(f"   👥 Conexiones enviadas: {self.stats['connections_sent']}")
            self.logger.info(f"   📨 Mensajes enviados: {self.stats['messages_sent']}")
            self.logger.info(f"   👀 Perfiles visitados: {self.stats['profiles_visited']}")
            self.logger.info(f"   ⏱️  Duración: {final_stats['duration_minutes']} minutos")
            self.logger.info("="*60)

# ============================================================================
# INTERFAZ DE USUARIO
# ============================================================================

def display_banner():
    """Mostrar banner de la aplicación"""
    
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     🚀 LINKEDIN AUTOMATION TOOL - VERSIÓN PRÁCTICA      ║
    ║                                                          ║
    ║     Herramienta segura para automatizar LinkedIn        ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    
    print(banner)

def interactive_mode():
    """Modo interactivo con menú"""
    
    display_banner()
    
    print("\n" + "="*60)
    print("📋 CONFIGURACIÓN INICIAL")
    print("="*60)
    
    # Cargar configuración si existe
    config_file = BASE_DIR / "config.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        accounts = config.get("accounts", [])
        if accounts:
            account = accounts[0]
            email = account["email"]
            password = account["password"]
            account_name = account.get("name", "default")
            
            print(f"\n📁 Configuración encontrada: {account_name}")
            print(f"   📧 Email: {email}")
            
            use_config = input("\n¿Usar configuración cargada? (s/n): ").strip().lower()
            
            if use_config == 's':
                bot = LinkedInBot(email, password, account_name)
            else:
                # Solicitar credenciales manualmente
                email = input("\n📧 Email de LinkedIn: ").strip()
                password = input("🔑 Contraseña: ").strip()
                account_name = input("👤 Nombre para esta cuenta (opcional): ").strip() or "default"
                bot = LinkedInBot(email, password, account_name)
        else:
            # No hay cuentas en la configuración
            email = input("\n📧 Email de LinkedIn: ").strip()
            password = input("🔑 Contraseña: ").strip()
            account_name = input("👤 Nombre para esta cuenta (opcional): ").strip() or "default"
            bot = LinkedInBot(email, password, account_name)
    else:
        # No existe archivo de configuración
        email = input("\n📧 Email de LinkedIn: ").strip()
        password = input("🔑 Contraseña: ").strip()
        account_name = input("👤 Nombre para esta cuenta (opcional): ").strip() or "default"
        bot = LinkedInBot(email, password, account_name)
    
    try:
        # Paso 1: Configurar navegador
        print("\n" + "="*60)
        print("⚙️  CONFIGURANDO NAVEGADOR")
        print("="*60)
        
        print("\n🔄 Inicializando ChromeDriver...")
        bot.setup_driver()
        
        # Paso 2: Login
        print("\n" + "="*60)
        print("🔐 INICIANDO SESIÓN")
        print("="*60)
        
        print("\n🔄 Conectando con LinkedIn...")
        if not bot.login():
            print("\n❌ No se pudo iniciar sesión. Verifica tus credenciales.")
            return
        
        # Menú principal
        while True:
            print("\n" + "="*60)
            print("📋 MENÚ PRINCIPAL")
            print("="*60)
            print("1. 🔍 Buscar perfiles y extraer información")
            print("2. 🤝 Enviar solicitudes de conexión")
            print("3. 🎯 Ejecutar campaña completa")
            print("4. 📊 Ver estadísticas actuales")
            print("5. 💾 Exportar datos de sesión")
            print("6. 🚪 Salir y cerrar sesión")
            print("="*60)
            
            choice = input("\n👉 Selecciona una opción (1-6): ").strip()
            
            if choice == "1":
                # Opción 1: Buscar perfiles
                print("\n" + "="*60)
                print("🔍 BUSCAR PERFILES")
                print("="*60)
                
                keyword = input("\nPalabra clave (ej: 'recruiter', 'developer'): ").strip()
                location = input("Ubicación (dejar vacío para mundial): ").strip()
                limit_input = input("Límite de resultados (default 50): ").strip()
                limit = int(limit_input) if limit_input.isdigit() else 50
                
                print(f"\n🔄 Buscando: '{keyword}' en '{location if location else 'todo el mundo'}'...")
                
                profiles = bot.search_people(keyword, location, limit)
                
                if profiles:
                    print(f"\n✅ Encontrados {len(profiles)} perfiles")
                    
                    # Preguntar si extraer información detallada
                    extract = input("\n¿Extraer información detallada de los primeros 10? (s/n): ").strip().lower()
                    
                    if extract == 's':
                        profiles_data = []
                        print("\n🔄 Extrayendo información...")
                        
                        for i, url in enumerate(profiles[:10]):
                            print(f"  📄 {i+1}/10: Extrayendo información...")
                            info = bot.extract_profile_info(url)
                            profiles_data.append(info)
                            time.sleep(1)  # Pequeña pausa entre extracciones
                        
                        # Guardar en CSV
                        save_csv = input("\n💾 ¿Guardar en archivo CSV? (s/n): ").strip().lower()
                        if save_csv == 's':
                            bot.save_profiles_to_csv(profiles_data)
                        
                        # Mostrar resumen
                        print(f"\n📋 Resumen extraído:")
                        for i, profile in enumerate(profiles_data[:3]):
                            print(f"  {i+1}. {profile.get('name', 'N/A')} - {profile.get('title', 'N/A')}")
                        if len(profiles_data) > 3:
                            print(f"  ... y {len(profiles_data) - 3} más")
                else:
                    print("\n❌ No se encontraron perfiles con esos criterios")
            
            elif choice == "2":
                # Opción 2: Enviar conexiones
                print("\n" + "="*60)
                print("🤝 ENVIAR CONEXIONES")
                print("="*60)
                
                keyword = input("\nPalabra clave para buscar perfiles: ").strip()
                location = input("Ubicación: ").strip()
                max_connections_input = input("Máximo de conexiones a enviar: ").strip()
                max_connections = int(max_connections_input) if max_connections_input.isdigit() else 10
                
                print(f"\n🔄 Buscando perfiles y enviando conexiones...")
                
                # Buscar perfiles
                profiles = bot.search_people(keyword, location, max_connections * 2)
                
                if not profiles:
                    print("\n❌ No se encontraron perfiles")
                    continue
                
                sent = 0
                failed = 0
                
                for i, url in enumerate(profiles[:max_connections]):
                    print(f"\n📄 Procesando perfil {i+1}/{min(max_connections, len(profiles))}")
                    result = bot.send_connection_request(url)
                    
                    if result.get('status') == 'sent':
                        sent += 1
                        print(f"  ✅ Conexión enviada exitosamente")
                    else:
                        failed += 1
                        print(f"  ❌ No enviada: {result.get('status')}")
                    
                    # Verificar si alcanzamos el máximo
                    if sent >= max_connections:
                        break
                
                print(f"\n" + "="*60)
                print(f"🎯 RESUMEN DE CONEXIONES")
                print("="*60)
                print(f"   ✅ Enviadas exitosamente: {sent}")
                print(f"   ❌ No enviadas: {failed}")
                print(f"   📊 Total procesadas: {sent + failed}")
                print(f"   🔄 Restantes hoy: {Config.DAILY_LIMITS['connection_requests'] - bot.daily_stats['connections']}")
            
            elif choice == "3":
                # Opción 3: Campaña completa
                print("\n" + "="*60)
                print("🎯 CAMPAÑA COMPLETA")
                print("="*60)
                
                keywords_input = input("\nPalabras clave (separar por comas): ").strip()
                keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
                
                locations_input = input("Ubicaciones (separar por comas, vacío para mundial): ").strip()
                locations = [l.strip() for l in locations_input.split(",")] if locations_input else []
                
                connections_input = input("Conexiones por día (default 30, máximo 40): ").strip()
                connections = int(connections_input) if connections_input.isdigit() else 30
                connections = min(connections, Config.DAILY_LIMITS['connection_requests'])
                
                messages_input = input("Mensajes por día (default 10, máximo 20): ").strip()
                messages = int(messages_input) if messages_input.isdigit() else 10
                messages = min(messages, Config.DAILY_LIMITS['messages'])
                
                print(f"\n" + "="*60)
                print("🚀 CONFIGURACIÓN DE CAMPAÑA")
                print("="*60)
                print(f"   📌 Keywords: {', '.join(keywords)}")
                print(f"   📍 Ubicaciones: {', '.join(locations) if locations else 'Mundial'}")
                print(f"   🤝 Objetivo conexiones: {connections}")
                print(f"   📨 Objetivo mensajes: {messages}")
                print("="*60)
                
                confirm = input("\n¿Iniciar campaña con esta configuración? (s/n): ").strip().lower()
                
                if confirm == 's':
                    print(f"\n🔄 Iniciando campaña...")
                    result = bot.run_campaign(keywords, locations, connections, messages)
                    
                    print(f"\n" + "="*60)
                    print("✅ CAMPAÑA COMPLETADA")
                    print("="*60)
                    print(f"   🤝 Conexiones enviadas: {result['connections_sent']}")
                    print(f"   📨 Mensajes enviados: {result['messages_sent']}")
                    print(f"   👀 Perfiles visitados: {result['profiles_visited']}")
                    print(f"   📊 Conexiones restantes hoy: {Config.DAILY_LIMITS['connection_requests'] - bot.daily_stats['connections']}")
                    print("="*60)
                else:
                    print("\n❌ Campaña cancelada")
            
            elif choice == "4":
                # Opción 4: Estadísticas
                print("\n" + "="*60)
                print("📊 ESTADÍSTICAS ACTUALES")
                print("="*60)
                
                # Estadísticas de sesión
                session_duration = datetime.now() - bot.stats['start_time']
                duration_minutes = round(session_duration.total_seconds() / 60, 1)
                
                print(f"\n⏱️  SESIÓN ACTUAL:")
                print(f"   Iniciada: {bot.stats['start_time'].strftime('%H:%M:%S')}")
                print(f"   Duración: {duration_minutes} minutos")
                print(f"   Acciones realizadas: {bot.stats['action_count']}")
                
                print(f"\n📈 ACTIVIDAD HOY ({bot.daily_stats['date']}):")
                print(f"   🤝 Conexiones enviadas: {bot.daily_stats['connections']}/{Config.DAILY_LIMITS['connection_requests']}")
                print(f"   📨 Mensajes enviados: {bot.daily_stats['messages']}/{Config.DAILY_LIMITS['messages']}")
                print(f"   👀 Perfiles visitados: {bot.daily_stats['profiles']}/{Config.DAILY_LIMITS['profile_visits']}")
                print(f"   🔍 Búsquedas realizadas: {bot.daily_stats['searches']}/{Config.DAILY_LIMITS['searches']}")
                
                # Calcular porcentajes
                conn_percentage = (bot.daily_stats['connections'] / Config.DAILY_LIMITS['connection_requests']) * 100
                msg_percentage = (bot.daily_stats['messages'] / Config.DAILY_LIMITS['messages']) * 100
                
                print(f"\n📊 PORCENTAJES DE USO:")
                print(f"   Conexiones: {conn_percentage:.1f}%")
                print(f"   Mensajes: {msg_percentage:.1f}%")
                
                # Recomendaciones
                print(f"\n💡 RECOMENDACIONES:")
                if conn_percentage > 80:
                    print("   ⚠️  Alto uso de conexiones - Considera reducir el ritmo")
                if msg_percentage > 80:
                    print("   ⚠️  Alto uso de mensajes - Considera reducir el ritmo")
                if bot.daily_stats['connections'] == 0:
                    print("   🎯 Puedes empezar a enviar conexiones")
                if bot.daily_stats['connections'] >= Config.DAILY_LIMITS['connection_requests']:
                    print("   ✅ Límite diario de conexiones alcanzado - Excelente trabajo!")
                
                input("\nPresiona Enter para continuar...")
            
            elif choice == "5":
                # Opción 5: Exportar datos
                print("\n" + "="*60)
                print("💾 EXPORTAR DATOS")
                print("="*60)
                
                print("\nSelecciona qué exportar:")
                print("1. 📊 Solo estadísticas")
                print("2. 📝 Solo logs")
                print("3. 📦 Todo (estadísticas + logs)")
                
                export_choice = input("\nOpción (1-3): ").strip()
                
                if export_choice == "1":
                    bot.export_session_data("stats")
                    print("✅ Estadísticas exportadas en carpeta 'exports/'")
                elif export_choice == "2":
                    bot.export_session_data("logs")
                    print("✅ Logs exportados en carpeta 'exports/'")
                elif export_choice == "3":
                    bot.export_session_data("all")
                    print("✅ Todos los datos exportados en carpeta 'exports/'")
                else:
                    print("❌ Opción inválida")
                
                input("\nPresiona Enter para continuar...")
            
            elif choice == "6":
                # Opción 6: Salir
                print("\n" + "="*60)
                print("👋 FINALIZANDO SESIÓN")
                print("="*60)
                
                confirm = input("\n¿Estás seguro de que quieres salir? (s/n): ").strip().lower()
                
                if confirm == 's':
                    print("\n🔄 Cerrando sesión...")
                    break
                else:
                    print("\n✅ Continuando con la sesión...")
            
            else:
                print("\n❌ Opción inválida. Por favor, selecciona 1-6.")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Sesión interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cerrar sesión siempre
        bot.close()

def auto_mode():
    """Modo automático que usa config.json"""
    
    display_banner()
    
    config_file = BASE_DIR / "config.json"
    
    if not config_file.exists():
        print("\n❌ ERROR: No se encontró config.json")
        print("\nPara usar el modo automático, primero crea el archivo de configuración:")
        print("  python src/linkedin_bot.py --setup")
        print("\nLuego edita config.json con tus credenciales y configuración.")
        return
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"\n❌ Error leyendo config.json: {e}")
        return
    
    accounts = config.get("accounts", [])
    campaigns = config.get("campaigns", [])
    
    if not accounts:
        print("\n❌ No hay cuentas configuradas en config.json")
        return
    
    if not campaigns:
        print("\n❌ No hay campañas configuradas en config.json")
        return
    
    print(f"\n📋 CONFIGURACIÓN CARGADA:")
    print(f"   📧 Cuentas: {len(accounts)}")
    print(f"   🎯 Campañas: {len(campaigns)}")
    
    # Procesar cada cuenta
    for account in accounts:
        print(f"\n" + "="*60)
        print(f"👤 PROCESANDO CUENTA: {account.get('name', 'default')}")
        print("="*60)
        
        bot = LinkedInBot(
            email=account["email"],
            password=account["password"],
            account_name=account.get("name", "default")
        )
        
        try:
            # Configurar navegador
            print("\n🔄 Configurando navegador...")
            bot.setup_driver()
            
            # Login
            print("🔐 Iniciando sesión...")
            if not bot.login():
                print(f"❌ Error en login para {account['email']}")
                continue
            
            # Ejecutar cada campaña
            for campaign in campaigns:
                print(f"\n" + "="*60)
                print(f"🎯 EJECUTANDO CAMPAÑA: {campaign['name']}")
                print("="*60)
                
                result = bot.run_campaign(
                    keywords=campaign["keywords"],
                    locations=campaign.get("locations", []),
                    connections_per_day=campaign.get("daily_connections", 25),
                    messages_per_day=campaign.get("daily_messages", 10)
                )
                
                print(f"\n✅ Campaña '{campaign['name']}' completada:")
                print(f"   🤝 Conexiones: {result['connections_sent']}")
                print(f"   📨 Mensajes: {result['messages_sent']}")
                
                # Pausa entre campañas (5 minutos)
                if campaign != campaigns[-1]:
                    print(f"\n⏸️  Pausa entre campañas: 5 minutos...")
                    time.sleep(300)
            
            print(f"\n✅ Cuenta '{account.get('name', 'default')}' procesada completamente")
            
        except Exception as e:
            print(f"\n❌ Error procesando cuenta {account['email']}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            bot.close()
    
    print(f"\n" + "="*60)
    print("🎉 TODAS LAS CUENTAS PROCESADAS")
    print("="*60)
    print("\n📊 Revisa los logs en la carpeta 'logs/' para ver los detalles.")

def setup_mode():
    """Modo de configuración inicial"""
    
    display_banner()
    
    print("\n" + "="*60)
    print("🛠️  CONFIGURACIÓN INICIAL")
    print("="*60)
    
    config_file = BASE_DIR / "config.json"
    
    if config_file.exists():
        print(f"\n⚠️  El archivo config.json ya existe.")
        overwrite = input("¿Deseas sobrescribirlo? (s/n): ").strip().lower()
        if overwrite != 's':
            print("\n✅ Configuración mantenida.")
            return
    
    # Crear configuración de ejemplo
    config = {
        "accounts": [
            {
                "email": "TU_EMAIL_AQUI@ejemplo.com",
                "password": "TU_CONTRASEÑA_AQUI",
                "name": "principal"
            }
        ],
        "campaigns": [
            {
                "name": "tech_recruiters_spain",
                "keywords": ["recruiter", "talent acquisition", "HR tech"],
                "locations": ["Spain"],
                "daily_connections": 25,
                "daily_messages": 10
            },
            {
                "name": "ctos_madrid",
                "keywords": ["CTO", "Chief Technology Officer", "VP Engineering"],
                "locations": ["Madrid"],
                "daily_connections": 20,
                "daily_messages": 5
            }
        ],
        "settings": {
            "max_runtime_hours": 3,
            "screenshot_errors": True,
            "save_profiles": True
        }
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Archivo config.json creado exitosamente")
        print(f"\n📍 Ruta: {config_file.absolute()}")
        
        print(f"\n📋 CONFIGURACIÓN CREADA:")
        print(f"   1. 📧 Cuenta: {config['accounts'][0]['email']}")
        print(f"   2. 🎯 Campañas: {len(config['campaigns'])}")
        
        print(f"\n⚠️  IMPORTANTE: Antes de usar el bot:")
        print(f"   1. Edita config.json con TU email y contraseña REALES")
        print(f"   2. Ajusta las campañas según tus necesidades")
        print(f"   3. Nunca compartas config.json con tus credenciales")
        
        print(f"\n🔧 Pasos siguientes:")
        print(f"   1. Edita config.json con un editor de texto")
        print(f"   2. Ejecuta: python src/linkedin_bot.py --auto")
        print(f"   3. O usa el modo interactivo: python src/linkedin_bot.py")
        
    except Exception as e:
        print(f"\n❌ Error creando config.json: {e}")

def show_help():
    """Mostrar ayuda"""
    
    display_banner()
    
    help_text = """
📖 AYUDA - LinkedIn Automation Tool

USO:
  python src/linkedin_bot.py          # Modo interactivo (recomendado para empezar)
  python src/linkedin_bot.py --auto   # Modo automático (usa config.json)
  python src/linkedin_bot.py --setup  # Crear config.json de ejemplo
  python src/linkedin_bot.py --help   # Mostrar esta ayuda

MODOS DE OPERACIÓN:

1. 🖥️  MODO INTERACTIVO:
   - Menú gráfico paso a paso
   - Control manual de cada acción
   - Ideal para aprender y probar
   - Recomendado para usuarios nuevos

2. 🤖 MODO AUTOMÁTICO:
   - Ejecución automática basada en config.json
   - Procesa múltiples cuentas y campañas
   - Ideal para uso programado/recurrente
   - Requiere configuración previa

3. 🛠️  MODO CONFIGURACIÓN:
   - Crea archivo config.json de ejemplo
   - Estructura básica lista para editar
   - Primer paso antes del modo automático

ARCHIVOS IMPORTANTES:

  📁 src/linkedin_bot.py      - Código principal del bot
  📁 scripts/                 - Scripts auxiliares
  📄 config.json              - Configuración (crear con --setup)
  📄 requirements.txt         - Dependencias de Python
  📄 README.md               - Documentación completa

CARPETAS GENERADAS:

  📁 data/                    - Perfiles exportados en CSV
  📁 logs/                    - Logs de actividad y estadísticas
  📁 exports/                 - Datos exportados
  📁 screenshots/             - Capturas de pantalla
  📁 chrome_profiles/         - Perfiles de Chrome por cuenta

CONSEJOS DE SEGURIDAD:

  1. 🔐 Usa tu cuenta REAL de LinkedIn
  2. ⚡ Respeta los límites diarios (40 conexiones/día máximo)
  3. ⏰ Ejecuta en horario laboral (9:00-18:00)
  4. 📊 Monitorea los logs regularmente
  5. 🚫 No abuses - más de 40 conexiones/día aumenta riesgo

PROBLEMAS COMUNES:

  ❌ ChromeDriver no funciona:
      Ejecuta: python scripts/install_chromedriver.py

  ❌ Error de login:
      1. Verifica credenciales en config.json
      2. Intenta login manual en LinkedIn primero
      3. Verifica que no haya CAPTCHA o verificación

  ❌ LinkedIn solicita verificación:
      1. Completa la verificación manualmente en el navegador
      2. El bot esperará 60 segundos para que lo hagas

MÁS INFORMACIÓN:

  📖 Documentación completa: README.md
  🐛 Reportar problemas: Issues en GitHub
  💡 Sugerencias: Pull Requests o Discussions

    """
    
    print(help_text)

# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

def main():
    """
    Función principal - Punto de entrada de la aplicación
    
    Controla los diferentes modos de operación basados en argumentos de línea de comandos
    """
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == "--auto":
            auto_mode()
        elif sys.argv[1] == "--setup":
            setup_mode()
        elif sys.argv[1] == "--help":
            show_help()
        else:
            print(f"\n❌ Argumento desconocido: {sys.argv[1]}")
            print("\nUso:")
            print("  python src/linkedin_bot.py          # Modo interactivo")
            print("  python src/linkedin_bot.py --auto   # Modo automático")
            print("  python src/linkedin_bot.py --setup  # Configuración inicial")
            print("  python src/linkedin_bot.py --help   # Ayuda")
    else:
        # Sin argumentos - modo interactivo por defecto
        interactive_mode()

# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    """
    Punto de ejecución principal.
    
    Este bloque asegura que el script solo se ejecute cuando es llamado directamente,
    no cuando es importado como módulo.
    """
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario. ¡Hasta pronto!")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Si el problema persiste, reporta el error en GitHub.")
        
