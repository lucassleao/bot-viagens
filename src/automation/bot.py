from dotenv import load_dotenv
import os

load_dotenv()

def processar_mensagem(texto):
    texto = texto.lower().strip()

    if "promoção" in texto or "promocao" in texto:
        return buscar_promocoes()

    elif "oi" in texto or "olá" in texto or "ola" in texto:
        return (
            "Olá! 👋\n"
            "Seja bem-vindo ao Bot de Viagens.\n\n"
            "Digite *promoção* para visualizar as ofertas disponíveis."
        )

    else:
        return (
            "Desculpe, não consegui identificar sua solicitação.\n\n"
            "Digite *promoção* para consultar as ofertas disponíveis."
        )