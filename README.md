# 🕵️‍♂️ Secret Stories

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flet 1.0.4](https://img.shields.io/badge/Flet-1.0.4-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flet.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg?style=for-the-badge)](LICENSE)

**Secret Stories** es una aplicación multiplataforma de juegos de acertijos y historias de misterio (inspirada en la mecánica clásica de *Black Stories* / *Dark Stories*), construida sobre **Python** y **Flet 1.0+** con soporte gráfico nativo de Flutter.

---

## ✨ Características Principales

- 🔄 **Sincronización Remota Automática:** Al abrir la aplicación, esta consulta de forma transparente el repositorio remoto de GitHub (`mikicolmena/Secret-Stories`) para descargar nuevas historias o imágenes sin necesidad de actualizar la aplicación manualmente.
- 📴 **Soporte Offline Garantizado:** Si no hay conexión a Internet, el programa utiliza automáticamente la copia local en caché de `stories.json`.
- 🃏 **Animación de Tarjeta Giratoria:** Transiciones fluidas con `AnimatedSwitcher` para revelar la solución del misterio al girar la tarjeta.
- 🌓 **Conmutador de Tema Claro / Oscuro:** Botón integrado en la cabecera para cambiar de tema visual instantáneamente.
- 📂 **Estructura Modular por Colecciones (DLCs):** Soporte multinivel para paquetes de historias independientes (ej. *Secret Stories #1*, *Secret Stories Reales #1*).

---

## 🛠️ Requisitos e Instalación

### Requisitos previos
- **Python 3.12** (Recomendado via `pyenv` en Linux/Ubuntu o ejecutable oficial en Windows/macOS).

### Paso a paso

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/mikicolmena/Secret-Stories.git](https://github.com/mikicolmena/Secret-Stories.git)
   cd Secret-Stories
