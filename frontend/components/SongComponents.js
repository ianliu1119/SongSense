import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";

// A single row in the Top-5 results list.
export function ResultRow({ song, onSave, onPlay }) {
  return (
    <View style={styles.row}>
      <TouchableOpacity onPress={() => onPlay?.(song)}>
        <Ionicons name="play-circle-outline" size={28} color="#3478F6" />
      </TouchableOpacity>
      <View style={styles.rowText}>
        <Text style={styles.title}>{song.title}</Text>
        <Text style={styles.sub}>
          {song.artist}
          {song.year ? ` · ${song.year}` : ""}
        </Text>
        {song.preview_url == null && (
          <Text style={styles.noPreview}>preview unavailable</Text>
        )}
      </View>
      <TouchableOpacity onPress={() => onSave?.(song)}>
        <Ionicons name="bookmark-outline" size={24} color="#888" />
      </TouchableOpacity>
    </View>
  );
}

// A saved-song card.
export function SavedCard({ song, onRemove }) {
  return (
    <View style={styles.card}>
      <Ionicons name="musical-notes-outline" size={22} color="#3478F6" />
      <View style={styles.rowText}>
        <Text style={styles.title}>{song.title}</Text>
        <Text style={styles.sub}>
          {song.artist}
          {song.year ? ` · ${song.year}` : ""}
        </Text>
      </View>
      <TouchableOpacity onPress={() => onRemove?.(song)}>
        <Ionicons name="bookmark" size={22} color="#3478F6" />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    paddingVertical: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: "#ddd",
  },
  card: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    padding: 12,
    marginBottom: 10,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: "#ddd",
    borderRadius: 12,
  },
  rowText: { flex: 1 },
  title: { fontSize: 15, fontWeight: "500", color: "#111" },
  sub: { fontSize: 12, color: "#666", marginTop: 2 },
  noPreview: { fontSize: 11, color: "#aaa", fontStyle: "italic", marginTop: 2 },
});
