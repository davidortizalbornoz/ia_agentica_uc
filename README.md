# Inteligencia Artificial Agéntica

Repositorio para incorporar los ejercicios propuestos y las partes guiadas del curso.

## Programa

Magíster en Inteligencia Artificial (MIA - UC)

Escuela de Ingeniería  
Pontificia Universidad Católica de Chile

**Curso:** Inteligencia Artificial Agéntica  
**Código:** INF3880

**Profesores:** Antonio Ossa y Vicente Dominguez  
**Ayudante:** Michelle Madrid

## Contenido

Cada clase vive en su propia carpeta. La clase 1 incluye el notebook de Colab, la parte guiada para ejecutar en local y los ejercicios.

| Recurso | Qué contiene |
| --- | --- |
| `CLASE_1/jupyter/` | Notebook de la primera llamada a un LLM, pensado para Colab. |
| `CLASE_1/parte_guiada/` | Script local de esa misma práctica, más `common.py` y `entorno_local.py`. |
| `CLASE_1/ejercicios/` | Ejercicios propuestos, cada uno con su script y su guía de ejecución. |

Las funciones compartidas (`leer_clave`, `elegir_modelo`, `generar`, `costo_usd` y `contar_tokens`) están en `CLASE_1/parte_guiada`. La key y la lista de modelos se leen desde un archivo `.env` en la raíz, a partir de `.env.sample`.

La forma de ejecutar cada recurso está al inicio de su markdown.
