#  LinkedIn Automation Tool

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-beta-yellow)

Una herramienta práctica de automatización para LinkedIn con comportamiento humano simulado y límites de seguridad integrados.

[Características](#-características) • [Instalación](#-instalación) • [Uso](#-uso) • [Advertencia](#-advertencia)

</div>

## 📋 Tabla de Contenidos
- [Características](#-características)
- [Advertencia](#-advertencia)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Ejemplos](#-ejemplos)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)
- [Disclaimer](#-disclaimer)

## ✨ Características

### 🤖 Automatización Inteligente
- **Comportamiento humano simulado**: Retardos variables, movimientos de ratón, scroll realista
- **Gestión de límites**: Respeto automático de los límites diarios de LinkedIn
- **Evitación de detección**: Técnicas para reducir el riesgo de detección como bot

### 🔒 Seguridad Integrada
- **Límites conservadores**: 40 conexiones/día (vs 100 permitidos por LinkedIn)
- **Pausas automáticas**: Descansos entre acciones simulando comportamiento humano
- **Gestión de errores**: Recuperación automática de errores comunes

### 📊 Gestión de Datos
- **Exportación CSV**: Guarda perfiles encontrados en formato estructurado
- **Logs detallados**: Registro completo de todas las actividades
- **Estadísticas**: Seguimiento de métricas y rendimiento

### 🛠️ Facilidad de Uso
- **Configuración simple**: Archivo JSON fácil de entender
- **Interfaz CLI**: Menú interactivo y comandos directos
- **Modo automático**: Ejecución programada de campañas

## ⚠️ ADVERTENCIA

**IMPORTANTE**: Esta herramienta debe usarse RESPONSABLEMENTE:

1. **Violación de TOS**: La automatización va contra los Términos de Servicio de LinkedIn
2. **Riesgo de cuenta**: Posible suspensión temporal o permanente de tu cuenta
3. **Uso ético**: No spamear, respetar límites, personalizar mensajes
4. **Propósito educativo**: Este proyecto es principalmente para fines educativos

**RECOMENDACIONES**:
- Usa una cuenta secundaria para pruebas
- No excedas los límites configurados
- Personaliza los mensajes de conexión
- Mantén intervalos humanos entre acciones

## 🚀 Instalación

### Prerrequisitos
- Python 3.8 o superior
- Google Chrome instalado
- Cuenta de LinkedIn (se recomienda secundaria para pruebas)

### Instalación Rápida

1. **Clonar el repositorio**:
```bash
git clone https://github.com/tuusuario/linkedin-automation-tool.git
cd linkedin-automation-tool
