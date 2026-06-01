require("dotenv").config();

const { searchFlights } = require("./src/api/flights");
const { formatFlightMessage } = require("./src/utils/messageParser");

function amanha() {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toISOString().split("T")[0]; // YYYY-MM-DD
}

async function main() {
  const origin = "GRU";
  const destination = "GIG";
  const date = amanha();
  const passengers = 1;

  console.log(`\nBuscando voos: ${origin} → ${destination} | ${date} | ${passengers} adulto\n`);

  try {
    const result = await searchFlights(origin, destination, date, passengers);
    console.log(formatFlightMessage(result));
  } catch (error) {
    console.error("Erro:", error.message);
  }
}

main();
