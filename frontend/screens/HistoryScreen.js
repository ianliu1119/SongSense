import React, { useState, useCallback } from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, Alert } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useFocusEffect } from "@react-navigation/native";
import { getHistory, getHistoryResults, saveSong, unsaveSong, getSaved, deleteHistory } from "../lib/api";
import { useAudioPlayer } from "../lib/useAudioPlayer";
import { ResultRow } from "../components/SongComponents";
import { C } from "../lib/theme";

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

  function confirmDelete(entry) {
    Alert.alert(
      "Delete search",
      `Remove "${entry.label}" from history?`,
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete", style: "destructive",
          onPress: async () => {
            await deleteHistory(entry.id);
            setItems((prev) => prev.filter((h) => h.id !== entry.id));
          },
        },
      ]
    );
  }

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
    } catch { return ""; }
  }

  const top = insets.top + 20;

  if (viewing) {
    return (
      <View style={[styles.container, { paddingTop: top }]}>
        <TouchableOpacity onPress={() => setViewing(null)} style={styles.backRow}>
          <View style={styles.backBtn}>
            <Ionicons name="chevron-back" size={18} color={C.primary} />
          </View>
          <Text style={styles.backLabel}>History</Text>
        </TouchableOpacity>
        <Text style={styles.heading}>{viewing.label}</Text>
        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 24 }}>
          {viewing.results.map((s) => (
            <ResultRow
              key={s.id}
              song={s}
              playing={playingId === s.id}
              initialSaved={savedIds.has(s.id)}
              onPlay={handlePlay}
              onSave={(song) => saveSong(song.id)}
              onUnsave={(song) => unsaveSong(song.id)}
            />
          ))}
        </ScrollView>
      </View>
    );
  }

  return (
    <View style={[styles.container, { paddingTop: top }]}>
      <Text style={styles.heading}>History</Text>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 24 }}>
        {items.length === 0 && (
          <View style={styles.emptyState}>
            <Ionicons name="time-outline" size={40} color={C.border} />
            <Text style={styles.emptyText}>No searches yet</Text>
            <Text style={styles.emptySub}>Your past searches will appear here</Text>
          </View>
        )}
        {items.map((h) => (
          <View key={h.id} style={styles.card}>
            <TouchableOpacity style={styles.cardMain} onPress={() => open(h)} activeOpacity={0.7}>
              <View style={styles.cardIcon}>
                <Ionicons name="search" size={16} color={C.primary} />
              </View>
              <View style={styles.cardText}>
                <Text style={styles.cardLabel} numberOfLines={1}>{h.label}</Text>
                <Text style={styles.cardTime}>{fmt(h.created_at)}</Text>
              </View>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => confirmDelete(h)} hitSlop={8} style={styles.deleteBtn}>
              <Ionicons name="trash-outline" size={16} color={C.sub} />
            </TouchableOpacity>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container:   { flex: 1, backgroundColor: C.bg, paddingHorizontal: 20 },
  heading:     { fontSize: 26, fontWeight: "800", color: C.text, letterSpacing: -0.5, marginBottom: 20 },
  backRow:     { flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 20 },
  backBtn:     { width: 32, height: 32, borderRadius: 10, backgroundColor: C.primaryLight,
                 alignItems: "center", justifyContent: "center" },
  backLabel:   { fontSize: 15, color: C.primary, fontWeight: "600" },
  card:        { flexDirection: "row", alignItems: "center", backgroundColor: C.card,
                 borderRadius: 16, marginBottom: 10,
                 shadowColor: "#000", shadowOpacity: 0.04, shadowRadius: 8, shadowOffset: { width: 0, height: 2 },
                 elevation: 2 },
  cardMain:    { flex: 1, flexDirection: "row", alignItems: "center", gap: 12, padding: 14 },
  cardIcon:    { width: 36, height: 36, borderRadius: 10, backgroundColor: C.primaryLight,
                 alignItems: "center", justifyContent: "center" },
  cardText:    { flex: 1 },
  cardLabel:   { fontSize: 15, fontWeight: "600", color: C.text },
  cardTime:    { fontSize: 12, color: C.sub, marginTop: 2 },
  deleteBtn:   { padding: 6 },
  emptyState:  { alignItems: "center", paddingTop: 80, gap: 8 },
  emptyText:   { fontSize: 17, fontWeight: "600", color: C.sub },
  emptySub:    { fontSize: 13, color: C.placeholder },
});
