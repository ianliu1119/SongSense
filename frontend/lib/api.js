import Constants from "expo-constants";

// Automatically use the same host Expo is running on.
// Works on physical devices, simulators, and web without any manual IP changes.
const host = Constants.expoConfig?.hostUri?.split(":")[0] ?? "localhost";
const BASE_URL = `http://${host}:8000`;

export async function search({ genre, lyric, extra, audioUri }) {
  const form = new FormData();
  form.append("genre", genre || "");
  form.append("lyric", lyric || "");
  form.append("extra", extra || "");
  if (audioUri) {
    form.append("audio", {
      uri: audioUri,
      name: "hum.m4a",
      type: "audio/m4a",
    });
  }
  const res = await fetch(`${BASE_URL}/search`, { method: "POST", body: form });
  const data = await res.json();
  return data.results;
}

export async function getHistory() {
  const res = await fetch(`${BASE_URL}/history`);
  return (await res.json()).history;
}

export async function getHistoryResults(id) {
  const res = await fetch(`${BASE_URL}/history/${id}`);
  return (await res.json()).results;
}

export async function deleteHistory(id) {
  await fetch(`${BASE_URL}/history/${id}`, { method: "DELETE" });
}

export async function getSaved() {
  const res = await fetch(`${BASE_URL}/saved`);
  return (await res.json()).saved;
}

export async function saveSong(id) {
  await fetch(`${BASE_URL}/saved/${id}`, { method: "POST" });
}

export async function unsaveSong(id) {
  await fetch(`${BASE_URL}/saved/${id}`, { method: "DELETE" });
}
