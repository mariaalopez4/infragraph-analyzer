# Reglas Operativas del Proyecto (AGENTS.md)

Este documento define las normas de desarrollo y conducta técnica para cualquier agente de IA o desarrollador que trabaje en el repositorio **InfraGraph Analyzer**.

---

## 1. Reglas de Operación y Control de Cambios

1. **Avance Atómico (1 archivo a la vez):**
   * No generes múltiples archivos de código en una sola respuesta a menos que se solicite explícitamente.
   * Crea o edita un componente por paso, explicando claramente qué hace y por qué.
2. **Pausa y Confirmación Obligatoria:**
   * Al completar una tarea o crear un archivo, detente y solicita confirmación/validación del usuario antes de pasar a la siguiente tarea.
3. **Comprensión Total del Código:**
   * Todo código introducido debe ser legible, autoexplicativo y modular. No usar trucos oscuros o atajos no documentados.

---

## 2. Estándares Tecnológicos y Comandos

- **Lenguaje:** Python 3.11+
- **Framework Web:** FastAPI (con routers modulares y OpenAPI/Swagger).
- **Validación y Modelado:** Pydantic v2 exclusivamente (uso de `BaseModel`, tipado estricto, sin sintaxis de Pydantic v1).
- **Linter & Formatter:** Ruff (`line-length = 88`, ordenamiento de imports `I`).
- **Base de Datos de Grafos:** Neo4j Community Edition (driver oficial `neo4j` para Python).
- **Testing:** `pytest` con pruebas unitarias y de integración bien delimitadas.
- **Comandos de validación obligatorios:** Antes de dar por cerrada una tarea de código, verificar con `ruff check .` y `pytest`.

---

## 3. Convenciones de Commits (Conventional Commits)

Todos los mensajes de Git deben seguir el estándar Conventional Commits:
- `feat: <descripción>` para nuevas funcionalidades.
- `fix: <descripción>` para corrección de errores.
- `docs: <descripción>` para cambios en documentación.
- `test: <descripción>` para añadir o modificar pruebas.
- `refactor: <descripción>` para reestructuración de código sin alterar comportamiento.
- `chore: <descripción>` para configuración de herramientas, dependencias o tareas auxiliares.

---

## 4. Filosofía del Alcance (Scope Discipline)

- **v1 (MVP Core):** Enfoque estricto en el motor algorítmico determinista (`shortestPath`, cuellos de botella), validación Pydantic, ingesta JSON y API REST desplegada con Docker Compose y datos seed.
- **v2 (Diferida):** Módulo GraphRAG (LLM / AI Explainer) y UI frontend interactiva. Prohibido adelantar código de v2 durante la v1.

---

## 5. Seguridad y Gestión de Secretos

- Prohibido escribir credenciales, URIs o contraseñas de Neo4j en texto plano dentro del código fuente.
- Toda configuración sensible debe leerse desde variables de entorno (`.env`, ignorado en Git) y documentarse con valores ficticios en `.env.example`.

---

## 6. Fuente de Verdad del Proyecto

- Antes de diseñar esquemas Pydantic, consultas Cypher o endpoints, consulta obligatoriamente los documentos de especificación en `docs/phase_1_benchmark_uvp.md` y `docs/phase_2_prd_data_model.md` (y el `README.md` cuando exista).