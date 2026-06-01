import requests
import os

def buscar_voo(texto):
    # tenta extrair origem
    origem = re.search(r"de (.+?) para", texto)
    # tenta extrair destino
    destino = re.search(r"para (.+?)( dia| $)", texto)
    # tenta extrair data
    data = re.search(r"dia (\d{2}/\d{2})", texto)

    if not origem or not destino:
        return (
            "Não entendi a rota. 😅\n\n"
            "Tente assim:\n"
            "*voo de São Paulo para Fortaleza dia 20/07*"
        )

    origem_texto = origem.group(1).strip()
    destino_texto = destino.group(1).strip()

    # busca código IATA dos aeroportos
    codigo_origem = buscar_codigo_iata(origem_texto)
    codigo_destino = buscar_codigo_iata(destino_texto)

    if not codigo_origem or not codigo_destino:
        return (
            f"Não encontrei o aeroporto de *{origem_texto}* ou *{destino_texto}*. 😅\n\n"
            "Tente usar cidades maiores ou verifique o nome."
        )

    # monta a data
    data_formatada = "2026-07-20"  # data padrão
    if data:
        partes = data.group(1).split("/")
        data_formatada = f"2026-{partes[1]}-{partes[0]}"

    # chama a API
    try:
        response = requests.post(
            "https://apidevoos.dev/flights/consulta-aereo/pesquisar",
            headers={
                "Authorization": f"Bearer {os.getenv('APIDEVOOS_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "origin": codigo_origem,
                "destination": codigo_destino,
                "departureDate": data_formatada,
                "adults": 1
            }
        )

        dados = response.json()

        if not dados.get("success") or not dados.get("data"):
            return (
                f"Não encontrei voos de *{origem_texto.title()}* para *{destino_texto.title()}* nessa data. 😕\n\n"
                "Tente outra data ou rota!"
            )

        voos = dados["data"][:3]  # pega os 3 primeiros
        resposta = f"✈️ *Voos de {origem_texto.title()} → {destino_texto.title()}*\n\n"

        for voo in voos:
            preco = voo.get("price", "N/A")
            cia = voo.get("airline", "N/A")
            horario = voo.get("departureTime", "N/A")
            resposta += f"🕐 {horario} | {cia} | 💰 R$ {preco}\n"

        resposta += (
            f"\n🔗 Ver mais opções:\n"
            f"https://www.google.com/travel/flights?q=voos+"
            f"{origem_texto.replace(' ', '+')}+para+{destino_texto.replace(' ', '+')}"
        )

        return resposta

    except Exception as e:
        return (
            "Tive um problema ao buscar os voos. 😕\n\n"
            "Tente novamente em instantes!"
        )


def buscar_codigo_iata(cidade):
    # tabela básica das principais cidades brasileiras
    cidades = {
        "são paulo": "GRU",
        "sao paulo": "GRU",
        "sp": "GRU",
        "rio": "GIG",
        "rio de janeiro": "GIG",
        "fortaleza": "FOR",
        "salvador": "SSA",
        "recife": "REC",
        "manaus": "MAO",
        "brasilia": "BSB",
        "brasília": "BSB",
        "belo horizonte": "CNF",
        "bh": "CNF",
        "curitiba": "CWB",
        "porto alegre": "POA",
        "belém": "BEL",
        "belem": "BEL",
        "natal": "NAT",
        "maceio": "MCZ",
        "maceió": "MCZ",
        "florianopolis": "FLN",
        "florianópolis": "FLN",
        "goiania": "GYN",
        "goiânia": "GYN",
    }
    return cidades.get(cidade.lower())