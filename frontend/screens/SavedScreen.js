import React, { useState, useCallback } from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useFocusEffect } from "@react-navigation/native";
import { getSaved, unsaveSong } from "../lib/api";
import { SavedCard } from "../components/SongComponents";

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
      <ScrollView>
        {songs.length === 0 && <Text style={styles.empty}>No saved songs yet.</Text>}
        {songs.map((s) => (
          <SavedCard key={s.id} song={s} onRemove={remove} />
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#fff" },
  heading: { fontSize: 22, fontWeight: "700", color: "#111", marginBottom: 16 },
  empty: { color: "#999", marginTop: 20 },
});
