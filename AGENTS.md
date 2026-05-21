# Reglas de Entorno y Ejecución (Project Context)

1. **Entorno Virtual Obligatorio:** Todo el desarrollo de Python de este proyecto utiliza un entorno virtual local ubicado en la carpeta `.venv` en la raíz del proyecto.
2. **Uso de dependencias:** NUNCA instales paquetes globales. Todas las instalaciones mediante `pip` deben hacerse activando primero el entorno virtual o usando directamente el ejecutable del entorno (ej. `.venv/Scripts/pip` en Windows).
3. **Ejecución de scripts:** Cuando necesites probar o ejecutar el servidor FastAPI, utiliza siempre el Python del entorno virtual (`.venv/Scripts/python` en Windows o `.venv/bin/python` en sistemas Unix).
4. **Sistema Operativo:** El entorno de desarrollo principal es Windows, tenlo en cuenta para las rutas de los archivos y los comandos de terminal.
5. **No alucinaciones de RVC:** El proyecto usa ESTRICTAMENTE la librería `rvc-python` de pip. No intentes clonar repositorios de GitHub antiguos ni usar WebUIs preexistentes.