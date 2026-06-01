from dotenv import load_dotenv
from flask import Flask, request, jsonify
import os
import re
import requests

load_dotenv()

app = Flask(__name__)

# RECEBE A MSG
@app.route("/mensagem", methods=["POST"])
def receber_mensagem():
    dados = request.json
    texto = dados.get("texto", "")
    resposta = processar_mensagem(texto)
    return jsonify({"resposta": resposta})

# LÓGICA
def processar_mensagem(texto):
    texto = texto.lower().strip()

    saudacoes = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "hello", "opa", "eai", "e aí"]
    if any(s in texto for s in saudacoes):
        return (
            "Olá! 👋\n\n"
            "Seja bem-vindo ao Bot de Viagens! ✈️\n\n"
            "Me diga para onde você quer ir e quando!\n\n"
            "Exemplos:\n"
            "• *voo de São Paulo para Fortaleza dia 20/07*\n"
            "• *quero viajar para o Rio dia 15/08*\n"
            "• *passagem de Manaus para Salvador*"
        )

    intencoes = ["voo", "voos", "passagem", "passagens", "voar", "viajar", "viagem", "quero ir", "quero viajar", "preciso ir", "bilhete"]
    if any(i in texto for i in intencoes):
        return buscar_voo(texto)

    promocoes_kw = ["promoção", "promocao", "promoções", "promocoes", "oferta", "ofertas", "barato", "barata", "desconto"]
    if any(p in texto for p in promocoes_kw):
        return (
            "🔥 *Voos em promoção hoje:*\n\n"
            "✈️ São Paulo → Fortaleza\n"
            "🔗 https://www.google.com/travel/flights?q=voos+sao+paulo+fortaleza\n\n"
            "✈️ Rio → Recife\n"
            "🔗 https://www.google.com/travel/flights?q=voos+rio+recife\n\n"
            "✈️ Brasília → Salvador\n"
            "🔗 https://www.google.com/travel/flights?q=voos+brasilia+salvador\n\n"
            "Quer buscar uma rota específica? Me diga a cidade de origem e destino! 😊"
        )

    ajuda_kw = ["ajuda", "help", "menu", "opções", "opcoes", "o que você faz", "o que voce faz", "como funciona"]
    if any(a in texto for a in ajuda_kw):
        return (
            "🤖 *Como eu funciono:*\n\n"
            "1️⃣ Me diga sua rota:\n"
            "   *voo de São Paulo para Fortaleza*\n\n"
            "2️⃣ Me diga o dia:\n"
            "   *dia 20/07*\n\n"
            "3️⃣ Eu te mando o link direto\n"
            "   para você ver os preços! ✈️\n\n"
            "Ou digite *promoções* para ver as ofertas do dia!"
        )

    return (
        "Não entendi. 😅\n\n"
        "Tente assim:\n"
        "• *voo de São Paulo para Fortaleza dia 20/07*\n"
        "• *promoções*\n"
        "• *ajuda*"
    )

# BUSCA 
def buscar_voo(texto):
    origem = re.search(r"de (.+?) para", texto)
    destino = re.search(r"para (.+?)( dia|$)", texto)
    data = re.search(r"dia (\d{2}/\d{2})", texto)

    if not origem or not destino:
        return (
            "Não entendi a rota. 😅\n\n"
            "Tente assim:\n"
            "*voo de São Paulo para Fortaleza dia 20/07*"
        )

    origem_texto = origem.group(1).strip()
    destino_texto = destino.group(1).strip()

    codigo_origem = buscar_codigo_iata(origem_texto)
    codigo_destino = buscar_codigo_iata(destino_texto)

    if not codigo_origem or not codigo_destino:
        return (
            f"Não encontrei o aeroporto de *{origem_texto}* ou *{destino_texto}*. 😅\n\n"
            "Tente usar o nome completo da cidade!"
        )

    data_formatada = "2026-07-20"
    if data:
        partes = data.group(1).split("/")
        data_formatada = f"2026-{partes[1]}-{partes[0]}"

    try:
        response = requests.post(
            "https://app.apidevoos.dev/api/v1/flights/search",
            headers={
                "Authorization": f"Bearer {os.getenv('APIDEVOOS_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "type": "one_way",
                "slices": [
                    {
                        "origin": codigo_origem,
                        "destination": codigo_destino,
                        "departureDate": data_formatada
                    }
                ],
                "passengers": [
                    {"type": "adult", "count": 1}
                ],
                "cabinClass": "economy",
                "searchType": "pagante"
            },
            timeout=30
        )

        dados = response.json()
        print("RESPOSTA API:", dados)

        if not dados.get("success") or not dados.get("flightGroups"):
            return (
                f"Não encontrei voos de *{origem_texto.title()}* para "
                f"*{destino_texto.title()}* nessa data. 😕\n\n"
                "Tente outra data ou rota!"
            )

        voos = dados["flightGroups"][:3]
        resposta = f"✈️ *Voos de {origem_texto.title()} → {destino_texto.title()}*\n\n"

        for voo in voos:
            preco = voo.get("totalPrice", {}).get("amount", "N/A")
            segmento = voo["slices"][0]["segments"][0]
            cia = segmento.get("airline", {}).get("name", "N/A")
            horario = segmento.get("departureTime", "N/A")[:16]
            duracao = segmento.get("duration", "N/A")
            resposta += f"🕐 {horario} | {cia} | ⏱ {duracao} | 💰 R$ {preco}\n\n"

        resposta += (
            f"🔗 Ver mais opções:\n"
            f"https://www.google.com/travel/flights?q=voos+"
            f"{origem_texto.replace(' ', '+')}+para+{destino_texto.replace(' ', '+')}"
        )

        return resposta

    except Exception as e:
        print(f"ERRO: {e}")
        return (
            "Tive um problema ao buscar os voos. 😕\n\n"
            "Tente novamente em instantes!"
        )

# ===== BUSCA CÓDIGO IATA (usando a linguagem do js)
def buscar_codigo_iata(cidade):
    try:
        response = requests.get(
            "https://app.apidevoos.dev/api/v1/airports/autocomplete",
            headers={
                "Authorization": f"Bearer {os.getenv('APIDEVOOS_KEY')}",
            },
            params={"q": cidade}
        )
        dados = response.json()
        print("IATA RESPOSTA:", dados)
        if dados and len(dados) > 0:
            return dados[0]["iata"]
        return None
    except Exception as e:
        print(f"ERRO IATA: {e}")
        return None

# da go no serv
if __name__ == "__main__":
    print("🤖 Bot de Viagens rodando na porta 5000...")
    app.run(port=5000, debug=True)