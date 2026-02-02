# 🤖 LinkedIn Automation Tool

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-beta-yellow)

Una herramienta práctica de automatización para LinkedIn con comportamiento humano simulado.

</div>

## ⚠️ ADVERTENCIA

**IMPORTANTE**: Esta herramienta debe usarse RESPONSABLEMENTE:
- Viola los Términos de Servicio de LinkedIn
- Puede resultar en suspensión de cuenta
- Úsala bajo tu propio riesgo
- Recomendado solo para fines educativos

## 🚀 Características

- **Comportamiento humano**: Retardos variables, escritura realista
- **Límites seguros**: 40 conexiones/día (vs 100 permitidos)
- **Gestión de sesiones**: Perfiles de Chrome persistentes
- **Logs detallados**: Registro completo de actividades
- **Configuración simple**: Archivo JSON fácil de editar

## 📦 Instalación

### 1. Prerrequisitos
```bash
# Python 3.8+
python --version

# Google Chrome instalado
```

2. Clonar e instalar
```bash
git clone https://github.com/tuusuario/linkedin-automation-tool.git
cd linkedin-automation-tool

# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno
python src/linkedin_bot.py --setup
```

3. Configurar
```bash
# Copiar y editar configuración
cp config.json.example config.json
# Edita config.json con tus credenciales
```

4. Instalar ChromeDriver (automático)
```bash
python scripts/install_chromedriver.py
```

🎯 Uso Básico

Modo Interactivo
```bash
python src/linkedin_bot.py
```

Comandos Directos
```bash
# Solo buscar perfiles
python src/linkedin_bot.py --search "CTO" --location "Madrid"

# Ejecutar campaña
python src/linkedin_bot.py --campaign "tech_spain"
```

⚙️ Configuración

Edita config.json:

```json
{
  "accounts": [
    {
      "email": "tu_email@ejemplo.com",
      "password": "tu_contraseña",
      "name": "principal"
    }
  ],
  "campaigns": [
    {
      "name": "tech_spain",
      "keywords": ["CTO", "Tech Lead"],
      "locations": ["Spain"],
      "daily_connections": 25
    }
  ]
}
```

📁 Estructura del Proyecto

```text
linkedin-automation-tool/
├── src/linkedin_bot.py          # Código principal
├── scripts/install_chromedriver.py
├── config.json.example         # Configuración de ejemplo
├── requirements.txt            # Dependencias
├── .gitignore                 # Archivos ignorados
├── LICENSE                    # Licencia MIT
└── README.md                  # Esta documentación
```

🛡️ Seguridad

NUNCA subas config.json a GitHub

Usa cuenta secundaria para pruebas

Respeta los límites configurados

Personaliza los mensajes de conexión

🤝 Contribuir

Haz fork del proyecto

Crea una rama: git checkout -b feature/nueva-funcionalidad

Commit: git commit -m 'Añadir funcionalidad'

Push: git push origin feature/nueva-funcionalidad

Abre un Pull Request

📄 Licencia

MIT License - ver LICENSE para detalles.

⚖️ Disclaimer

Este software se proporciona "TAL CUAL", sin garantías. El autor no se hace responsable del mal uso de esta herramienta.


<div align="center"> Hecho para Mi equipo de trabajo CHC Asesorias </div>




🚀 COMANDOS PARA SUBIR A GITHUB
```bash
# 1. Inicializar repositorio
git init

# 2. Añadir archivos
git add .

# 3. Primer commit
git commit -m "Initial commit: LinkedIn Automation Tool v1.0"

# 4. Crear repositorio en GitHub (desde website)
#    https://github.com/new
#    Nombre: linkedin-automation-tool
#    Sin README, .gitignore ni LICENSE (ya los tenemos)

# 5. Añadir remoto
git remote add origin https://github.com/TU_USUARIO/linkedin-automation-tool.git

# 6. Renombrar rama a main
git branch -M main

# 7. Subir
git push -u origin main
```
