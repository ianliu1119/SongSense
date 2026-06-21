import React, { useState, useCallback } from "react";
import {
  View, Text, TouchableOpacity, ScrollView, StyleSheet,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useFocusEffect } from "@react-navigation/native";
import { getHistory, getHistoryResults, saveSong, unsaveSong, getSaved } from "../lib/api";
import { useAudioPlayer } from "../lib/useAudioPlayer";
import { ResultRow } from "../components/SongComponents";

export default function HistoryScreen() {
  const insets = useSafeAreaInsets();
  const { playingId, handlePlay } = useAudioPlayer();
  const [items, setItems] = useState([]);
  const [viewing, setViewing] = useState(null);
  const [savedIds, setSavedIds] = useState(new Set());

  useFocusEffect(
    useCallback(() => {
      getHistory().then(setItems).catch(() => {});
    }, [])
  );

  async function open(entry) {
    const [results, saved] = await Promise.all([
      getHistoryResults(entry.id),
      getSaved(),
    ]);
    setSavedIds(new Set(saved.map((s) => s.id)));
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
      <View style={[styles.container, { paddingTop: insets.top + 20 }]}>
        <TouchableOpacity onPress={() => setViewing(null)} style={styles.back}>
          <Ionicons name="arrow-back" size={18} color="#3478F6" />
          <Text style={styles.backText}>back</Text>
        </TouchableOpacity>
        <Text style={styles.heading}>{viewing.label}</Text>
        <ScrollView>
          {viewing.results.map((s) => (
            <ResultRow key={s.id} song={s} playing={playingId === s.id} initialSaved={savedIds.has(s.id)} onPlay={handlePlay} onSave={(song) => saveSong(song.id)} onUnsave={(song) => unsaveSong(song.id)} />
          ))}
        </ScrollView>
      </View>
    );
  }

  return (
    <View style={[styles.container, { paddingTop: insets.top + 20 }]}>
      <Text style={styles.heading}>History</Text>
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
  heading: { fontSize: 22, fontWeight: "700", color: "#111", marginBottom: 16 },
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
