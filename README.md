# Inteligencia Artificial Agéntica

Repositorio de las partes guiadas y los ejercicios del curso. Cada clase vive en su carpeta. La forma de ejecutar cada script local está al inicio del markdown del mismo nombre.

**Dueño del repositorio:**

David Ortiz Albornoz  
dortiza@uc.cl  
david.ortiz.albornoz@gmail.com

## Programa

Magíster en Inteligencia Artificial (MIA - UC)

Escuela de Ingeniería  
Pontificia Universidad Católica de Chile

**Curso:** Inteligencia Artificial Agéntica  
**Código:** INF3880

**Profesores:** Antonio Ossa y Vicente Dominguez  
**Ayudante:** Michelle Madrid

## Inventario

En la raíz están `.env.sample`, `.python-version` (entorno pyenv `ia_agentica_uc`, Python 3.13.5) y este archivo. Los scripts que llaman al modelo leen `GEMINI_API_KEY` y `PREFERIDOS` desde el `.env` de la raíz, con `leer_clave` de `CLASE_1/parte_guiada/entorno_local.py`. La llamada, el modelo elegido y el costo están en `CLASE_1/parte_guiada/common.py`.

### CLASE_1

Primera llamada a un modelo: tokens, costo y `temperature`.

| Recurso | Qué contiene |
| --- | --- |
| `CLASE_1/jupyter/1_practico_primera_llamada_a_un_llm.ipynb` | Notebook del práctico 1. |
| `CLASE_1/parte_guiada/1_practico_primera_llamada_a_un_llm.py` | La misma práctica en local: respuesta a «¿Qué es un token?», tokens, costo y `temperature` 0.0 y 1.0. |
| `CLASE_1/parte_guiada/common.py` | `elegir_modelo`, `generar`, `costo_usd` y `contar_tokens`. |
| `CLASE_1/parte_guiada/entorno_local.py` | Lectura del `.env`. |

#### Ejercicios

| Recurso | Qué hace |
| --- | --- |
| `CLASE_1/ejercicios/1_ejercicio_tabla_temperature.py` | La misma consulta con `temperature` 0.0, 0.7 y 1.0. Imprime `temperature`, `tokens_salida` y `respuesta`. |
| `CLASE_1/ejercicios/2_ejercicio_costo_1000_consultas.py` | Compara el modelo elegido con `gemini-3.8-flash` en tokens y costo de 1.000 consultas al día por 30 días. La segunda tabla deja la salida medida y pone la entrada en 2000 tokens. |
| `CLASE_1/ejercicios/3_ejercicio_salida_json.py` | Tres frases a un objeto JSON con `producto`, `cantidad` y `ciudad`. |

### CLASE_2

System prompts medidos sobre correos ya etiquetados, y salidas validadas con Pydantic.

| Recurso | Qué contiene |
| --- | --- |
| `CLASE_2/jupyter/2_practico_system_prompts_que_se_prueban.ipynb` | Notebook del práctico 2: tres system prompts y una salida estructurada. |
| `CLASE_2/parte_guiada/1_practico_elproblema_ylosdatos.py` | 31 correos de Andina Cargo, con `clasificacion` (`facturacion`, `tecnico`, `reclamo`, `otro`) y `dificultad` (`facil`, `dificil`). |
| `CLASE_2/parte_guiada/2_practico_3versionesde_systemprompt.py` | Clasifica esos 31 correos con `v1_vago`, `v2_estructurado` y `v3_con_ejemplos`, 3 ciclos por versión. |
| `CLASE_2/parte_guiada/3_practico_salidas_estructuradas_pydantic.py` | Esquema `Clasificacion`: `categoria`, `urgencia` y `resumen`. |

#### Ejercicios

| Recurso | Qué hace |
| --- | --- |
| `CLASE_2/ejercicios/1_ejercicio_subir_exactitud_casos_dificiles.py` | Agrega `v4_mejorado`, con reglas de desempate y ejemplos de casos trampa, y vuelve a medir los 31 correos. |
| `CLASE_2/ejercicios/2_ejercicio_aplicar_razonamiento.py` | Compara `v2_estructurado` con la misma instrucción y razonamiento alto. Suma tokens de respuesta y de razonamiento, y estima el costo. |
| `CLASE_2/ejercicios/3_ejercicio_extraccion_estructurada_pedidos.py` | Siete frases a un objeto `Pedido` con `sku`, `cantidad` y `ciudad`. |
| `CLASE_2/ejercicios/4_ejercicio_casos_tickets_jira.py` | 18 tickets con `contexto`, `categoria` (`desarrollo`, `despliegue`, `monitoreo`) y `prioridad` (`alta`, `media`, `baja`). |
| `CLASE_2/ejercicios/5_ejercicio_medicion_prompts.py` | Asigna la prioridad de esos 18 tickets con `v2_estructurado` y `v3_con_ejemplos`, 3 ciclos por versión. |

## API key

La key se crea en Google AI Studio. Los notebooks la leen desde Secrets. Los scripts locales la leen desde el `.env` de la raíz.

### Paso A · Crear la key en Google AI Studio

1. Abre **https://aistudio.google.com/apikey** e inicia sesión con tu cuenta de Google (personal; la cuenta institucional puede tener AI Studio bloqueado).
2. La primera vez te pedirá aceptar los términos de servicio de la Gemini API. Al aceptarlos, Google crea un proyecto por defecto.
3. Haz clic en **Create API key** (si ya tienes un proyecto, elige **Create API key in existing project** o el proyecto por defecto).
4. Copia la key con **Copiar clave** (las keys actuales empiezan con `AQ.`; las antiguas con `AIza`). Si la pierdes, puedes crear otra desde la misma página.
5. Opcional: en la lista de keys, pasa el mouse sobre **Unrestricted** → **Add restrictions** → **Restrict to Gemini API only** → **Restrict key**.

Los límites y el uso están en AI Studio, menú lateral → **Dashboard** → **Usage & Billing** (https://aistudio.google.com/usage). Documentación: https://ai.google.dev/gemini-api/docs/api-key

### Paso B · Guardar la key en Secrets de Colab

1. En el notebook, haz clic en el ícono de la llave de la barra lateral izquierda (**Secrets**).
2. **+ Add new secret**: en *Name* escribe exactamente `GEMINI_API_KEY`; en *Value* pega la key.
3. Activa **Notebook access** para ese notebook.
4. No pegues la key en una celda, no la subas al repositorio y no la compartas. Si se filtra, crea una nueva y borra la antigua en AI Studio.

### Scripts locales

```bash
cp .env.sample .env
```

Abre `.env` y reemplaza el valor de `GEMINI_API_KEY`. `PREFERIDOS` ya trae la lista de modelos, separados por coma y en orden de preferencia. El script usa el primero que esté disponible en el proyecto.
