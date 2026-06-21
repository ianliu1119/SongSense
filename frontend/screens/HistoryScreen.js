import React, { useState, useCallback } from "react";
import {
  View, Text, TouchableOpacity, ScrollView, StyleSheet,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useFocusEffect } from "@react-navigation/native";
import { getHistory, getHistoryResults, saveSong } from "../lib/api";
import { ResultRow } from "../components/SongComponents";

export default function HistoryScreen() {
  const [items, setItems] = useState([]);
  const [viewing, setViewing] = useState(null); // {label, results}

  useFocusEffect(
    useCallback(() => {
      getHistory().then(setItems).catch(() => {});
    }, [])
  );

  async function open(entry) {
    const results = await getHistoryResults(entry.id);
    setViewing({ label: entry.label, results });
  }

  function fmt(iso) {
    try {
      const d = new Date(iso);
      return d.toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    } catch {
      return "";
    }
  }

  if (viewing) {
    return (
      <View style={styles.container}>
        <TouchableOpacity onPress={() => setViewing(null)} style={styles.back}>
          <Ionicons name="arrow-back" size={18} color="#3478F6" />
          <Text style={styles.backText}>back</Text>
        </TouchableOpacity>
        <Text style={styles.heading}>{viewing.label}</Text>
        <ScrollView>
          {viewing.results.map((s) => (
            <ResultRow key={s.id} song={s} onSave={(song) => saveSong(song.id)} />
          ))}
        </ScrollView>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Search history</Text>
      <ScrollView>
        {items.length === 0 && <Text style={styles.empty}>No searches yet.</Text>}
        {items.map((h) => (
          <TouchableOpacity key={h.id} style={styles.row} onPress={() => open(h)}>
            <Text style={styles.label}>{h.label}</Text>
            <Text style={styles.time}>{fmt(h.created_at)}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#fff" },
  heading: { fontSize: 18, fontWeight: "600", marginBottom: 12 },
  row: {
    flexDirection: "row", justifyContent: "space-between", alignItems: "center",
    paddingVertical: 14, borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: "#ddd",
  },
  label: { fontSize: 15, fontWeight: "500", color: "#111" },
  time: { fontSize: 12, color: "#888" },
  empty: { color: "#999", marginTop: 20 },
  back: { flexDirection: "row", alignItems: "center", gap: 4, marginBottom: 8 },
  backText: { color: "#3478F6", fontSize: 14 },
});
