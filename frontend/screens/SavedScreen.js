import React, { useState, useCallback } from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useFocusEffect } from "@react-navigation/native";
import { getSaved, unsaveSong } from "../lib/api";
import { SavedCard } from "../components/SongComponents";
import { C } from "../lib/theme";

export default function SavedScreen() {
  const insets = useSafeAreaInsets();
  const [songs, setSongs] = useState([]);

  const load = useCallback(() => {
    getSaved().then(setSongs).catch(() => {});
  }, []);

  useFocusEffect(load);

  async function remove(song) {
    await unsaveSong(song.id);
    setSongs((s) => s.filter((x) => x.id !== song.id));
  }

  return (
    <View style={[styles.container, { paddingTop: insets.top + 20 }]}>
      <Text style={styles.heading}>Saved</Text>
      {songs.length > 0 && (
        <Text style={styles.count}>{songs.length} song{songs.length !== 1 ? "s" : ""}</Text>
      )}
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 24 }}>
        {songs.length === 0 && (
          <View style={styles.emptyState}>
            <Ionicons name="bookmark-outline" size={40} color={C.border} />
            <Text style={styles.emptyText}>No saved songs yet</Text>
            <Text style={styles.emptySub}>Bookmark songs from your search results</Text>
          </View>
        )}
        {songs.map((s) => (
          <SavedCard key={s.id} song={s} onRemove={remove} />
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container:  { flex: 1, backgroundColor: C.bg, paddingHorizontal: 20 },
  heading:    { fontSize: 26, fontWeight: "800", color: C.text, letterSpacing: -0.5 },
  count:      { fontSize: 13, color: C.sub, marginTop: 2, marginBottom: 16 },
  emptyState: { alignItems: "center", paddingTop: 80, gap: 8 },
  emptyText:  { fontSize: 17, fontWeight: "600", color: C.sub },
  emptySub:   { fontSize: 13, color: C.placeholder },
});
