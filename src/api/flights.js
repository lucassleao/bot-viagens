require("dotenv").config();
const axios = require("axios");

const client = axios.create({
  baseURL: "https://app.apidevoos.dev/api/v1",
  headers: {
    Authorization: `Bearer ${process.env.APIDEVOOS_KEY}`,
    "Content-Type": "application/json",
  },
});

async function searchFlights(origin, destination, date, passengers) {
  try {
    const { data } = await client.post("/flights/search", {
      type: "one_way",
      slices: [{ origin, destination, departureDate: date }],
      passengers: [{ type: "adult", count: passengers }],
    });
    return data;
  } catch (error) {
    throw new Error(
      `Erro ao buscar voos: ${error.response?.data?.message ?? error.message}`
    );
  }
}

async function searchAirports(query) {
  try {
    const { data } = await client.get("/airports/autocomplete", {
      params: { q: query },
    });
    return data;
  } catch (error) {
    throw new Error(
      `Erro ao buscar aeroportos: ${error.response?.data?.message ?? error.message}`
    );
  }
}

async function getOffers() {
  try {
    const { data } = await client.get("/flights/offers");
    return data;
  } catch (error) {
    throw new Error(
      `Erro ao buscar ofertas: ${error.response?.data?.message ?? error.message}`
    );
  }
}

module.exports = { searchFlights, searchAirports, getOffers };
