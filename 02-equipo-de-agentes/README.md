# 02 · Tu primer equipo de agentes
### De "un chatbot que responde" a un equipo de agentes con roles que ejecuta una tarea de principio a fin

**Categoría:** Agentes · **Estado:** En producción · **Nivel:** intermedio

Una guía para que **vos lo armes y experimentes**: pasás de prompts sueltos a un sistema donde varios agentes especializados (Investiga, Analiza, Construye, Valida) se reparten el trabajo, comparten un estado y devuelven un resultado verificable.

## Qué vas a lograr
Un **orquestador** que recibe una tarea, la reparte entre agentes con un rol claro, les pasa contexto por un `state` compartido, usa herramientas (código determinista) y valida el resultado. Queda claro qué es **criterio del modelo** y qué es **código**.

## La idea en una imagen
```
tarea → [Investiga] → [Analiza] → [Construye] → [Valida] → resultado
            │ usa tools (código)        state compartido entre todos
```

## Corré el ejemplo en 10 segundos
El kit trae `orchestrator.py` — **solo librería estándar de Python** (nada que instalar). Corre en **modo MOCK** sin API key:
```bash
cd kit
python3 orchestrator.py "Planea el lanzamiento de mi newsletter"
```
Vas a ver cada agente tomando el trabajo del anterior. Para respuestas reales, poné tu `OPENAI_API_KEY` (ver `kit/.env.example`); funciona con cualquier API estilo OpenAI.

## Las 3 decisiones que importan
1. **Roles con una responsabilidad cada uno.** Un agente que hace todo = un prompt gigante frágil. Dividí por verbo: *investiga / analiza / construye / valida*.
2. **Estado compartido explícito.** Los agentes se pasan un `state` (dict), no "se adivinan". Eso lo hace depurable.
3. **Determinista vs criterio.** Lo que se puede calcular (buscar, formatear, validar formato) va en **código/tools**; el juicio va en el **modelo**.

## Control de costo, latencia y errores
- Menos pasos y modelo más chico donde alcance.
- **Cortá temprano**: si `Valida` responde OK, no sigas.
- Reintentos con límite y *timeout* en cada llamada (no loops infinitos).
- Medí: tokens/corrida y tiempo por agente.

## Cómo extenderlo
- **Nuevo agente:** una función `def x(state): ...` sumada a `AGENTES`.
- **Nueva herramienta:** una función determinista que el agente invoca.
- **Router:** en vez de secuencia fija, un agente que decide a quién llamar según la tarea.

## Descargas
Kit en `kit/` (orchestrator.py, .env.example, requirements, README) y el **ZIP** con todo. Combinalo con el **10 · Prompts que se comportan como software** para salidas tipadas y evals.

---
Hecho por **Esteban Baquero** · [estebanbaquero.com](https://estebanbaquero.com) · De una idea a un sistema que funciona.
Si te sirvió, **seguime y dale ⭐** → [github.com/Estebens22](https://github.com/Estebens22)
