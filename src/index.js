require("dotenv").config();
const express = require("express");
const { searchFlights } = require("./api/flights");
const { extractFlightInfo, formatFlightMessage, formatDate } = require("./utils/messageParser");

const app = express();
app.use(express.json());

const HELP_MESSAGE =
  "Olá! Para buscar voos me diga: de onde vai partir, para onde vai e a data. " +
  "Exemplo: quero voar de GRU para GIG dia 15/07 ✈️";

function tomorrow() {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toISOString().split("T")[0]; // YYYY-MM-DD
}

app.post("/webhook", async (req, res) => {
  const { phone, message } = req.body ?? {};

  const { origin, destination, date } = extractFlightInfo(message ?? "");

  if (!origin || !destination) {
    return res.json({ phone, reply: HELP_MESSAGE });
  }

  const searchDate = date ? formatDate(date) : tomorrow();

  try {
    const result = await searchFlights(origin, destination, searchDate, 1);
    const reply = formatFlightMessage(result);
    return res.json({ phone, reply });
  } catch {
    return res.json({
      phone,
      reply: "Desculpe, não consegui buscar os voos agora. Tente novamente em instantes.",
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});
