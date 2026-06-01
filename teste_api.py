import requests
import os
from dotenv import load_dotenv

load_dotenv()

r = requests.post(
    "https://app.apidevoos.dev/api/flights/consulta-aereo/aeroportos?filtro=sao paulo",
    headers={
        "Authorization": f"Bearer {os.getenv('APIDEVOOS_KEY')}",
    }
)

print("Status:", r.status_code)
print("Resposta:", r.text) 