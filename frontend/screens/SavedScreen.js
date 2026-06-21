import React, { useState, useCallback } from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { getSaved, unsaveSong } from "../lib/api";
import { SavedCard } from "../components/SongComponents";

export default function SavedScreen() {
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
    <View style={styles.container}>
      <Text style={styles.heading}>Saved songs</Text>
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
  heading: { fontSize: 18, fontWeight: "600", marginBottom: 12 },
  empty: { color: "#999", marginTop: 20 },
});
