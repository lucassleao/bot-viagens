"use strict";

// Captura "de <origem> para <destino>" e para antes de palavra-chave de data,
// pontuação ou fim de string — funciona com IATA (GRU) e nomes de cidade.
function extractFlightInfo(message) {
  const info = { origin: null, destination: null, date: null };

  const routeMatch = message.match(
    /\bde\s+(.+?)\s+para\s+(.+?)(?=\s+(?:(?:no\s+)?dia|em)\b|[,.]|$)/i
  );

  if (routeMatch) {
    info.origin = routeMatch[1].trim();
    info.destination = routeMatch[2].trim();
  }

  // Aceita DD/MM, DD/MM/YY e DD/MM/YYYY
  const dateMatch = message.match(/\b(\d{1,2}\/\d{2}(?:\/\d{2,4})?)\b/);
  if (dateMatch) {
    info.date = dateMatch[1];
  }

  return info;
}

function formatFlightMessage({ flightGroups } = {}) {
  if (!flightGroups?.length) {
    return "✈️ Nenhum voo encontrado para essa rota.";
  }

  const items = flightGroups.slice(0, 5).map((group, i) => {
    const segment =
      group.flightInfo?.itineraries?.[0]?.segments?.[0] ?? {};
    const departure = segment.departure?.time ?? "--:--";
    const arrival = segment.arrival?.time ?? "--:--";

    const minPrice = Math.min(
      ...group.offers.map((o) => o.price?.total ?? Infinity)
    );
    const priceLabel = (minPrice / 100).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });

    return (
      `✈️ *Voo ${i + 1}*\n` +
      `🛫 Partida: ${departure}\n` +
      `🛬 Chegada: ${arrival}\n` +
      `💰 A partir de ${priceLabel}\n` +
      `---`
    );
  });

  return items.join("\n");
}

function formatDate(dateStr) {
  const [day, month, rawYear] = dateStr.split("/");

  const year = !rawYear
    ? new Date().getFullYear()
    : rawYear.length === 2
    ? Number(`20${rawYear}`)
    : Number(rawYear);

  return `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`;
}

module.exports = { extractFlightInfo, formatFlightMessage, formatDate };
