import time

from common import MODEL, contar_tokens, costo_usd, generar

if __name__ == "__main__":
    print("\nSECCION 1. ELECCION DEL MODELO")
    print("______________________________________________\n")

    print("Listo. Modelo:", MODEL)
    print("\n")


    print("SECCION 2. PETICION A LLM")
    print("______________________________________________\n")

    inicio = time.perf_counter()
    respuesta = generar(
        "¿Qué es un token?",
        system_instruction="Eres un tutor de un curso de IA agéntica. Respondes en español, en máximo 3 frases.",
        temperature=0.2,
        max_output_tokens=200,
    )
    print(respuesta.text)
    print(f"tiempo de respuesta: {(time.perf_counter() - inicio) * 1000:.0f} ms")
    print("\n")

    print("SECCION 3. RESUMEN DE COSTOS")
    print("______________________________________________\n")

    u = respuesta.usage_metadata
    if u is None:
        raise SystemExit("La respuesta del modelo llegó sin datos de uso.")
    print("tokens de entrada (prompt)   :", u.prompt_token_count)
    print("tokens de salida (respuesta) :", u.candidates_token_count)
    print("tokens de razonamiento       :", u.thoughts_token_count or 0, "  <- algunos modelos 'piensan' antes de responder y eso también son tokens")
    print("total                        :", u.total_token_count)
    salida = (u.candidates_token_count or 0) + (u.thoughts_token_count or 0)
    print(f"costaría (nivel de pago)     : US${costo_usd(u.prompt_token_count, salida):.6f}")
    print("\n")

    print("SECCION 4. CONTABILIZAR TOKENS EN BASE A TEXTO")
    print("______________________________________________\n")

    # ¿Cuántos tokens ocupa un texto? Gemini permite contarlos sin generar nada (y sin consumir cuota de generación).
    for t in ["Hola", "Los agentes usan herramientas.", "Agents use tools.", "Supercalifragilístico"]:
        print(f"{t!r:40} -> {contar_tokens(t)} tokens")
    print("\n")

    print("SECCION 5. TEMPERATURA (ALEATORIEDAD)")
    print("______________________________________________\n")

    prompt = "Propón un eslogan de máximo 8 palabras para una cafetería de barrio. Responde solo con el eslogan."

    for temp in [0.0, 1.0]:
        print(f"--- temperature={temp} ---")
        for _ in range(3):
            r = generar(prompt, temperature=temp, max_output_tokens=40)
            texto = r.text
            if texto is None:
                raise SystemExit("La respuesta del modelo llegó sin texto.")
            print(" ·", texto.strip())

    print("\n FIN SCRIPT")