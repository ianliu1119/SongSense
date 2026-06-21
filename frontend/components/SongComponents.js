import React, { useState } from "react";
import { View, Text, TouchableOpacity, Image, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";

const ARTWORK_SIZE = 52;

function ArtworkWithPlay({ artworkUrl, canPlay, playing, onPress }) {
  return (
    <TouchableOpacity onPress={onPress} disabled={!canPlay} style={styles.artworkWrapper}>
      {artworkUrl ? (
        <Image source={{ uri: artworkUrl }} style={styles.artwork} />
      ) : (
        <View style={[styles.artwork, styles.artworkPlaceholder]}>
          <Ionicons name="musical-note" size={22} color="#bbb" />
        </View>
      )}
      <View style={styles.playOverlay}>
        <Ionicons
          name={playing ? "pause-circle" : "play-circle"}
          size={28}
          color={canPlay ? "rgba(255,255,255,0.95)" : "rgba(255,255,255,0.35)"}
        />
      </View>
    </TouchableOpacity>
  );
}

// A single row in the Top-5 results list.
export function ResultRow({ song, onSave, onUnsave, onPlay, playing, initialSaved }) {
  const [saved, setSaved] = useState(initialSaved ?? false);
  const canPlay = !!song.preview_url;

  function handleBookmark() {
    const next = !saved;
    setSaved(next);
    if (next) onSave?.(song);
    else onUnsave?.(song);
  }

  return (
    <View style={styles.row}>
      <ArtworkWithPlay
        artworkUrl={song.artwork_url}
        canPlay={canPlay}
        playing={playing}
        onPress={() => onPlay?.(song)}
      />
      <View style={styles.rowText}>
        <Text style={styles.title} numberOfLines={1}>{song.title}</Text>
        <Text style={styles.sub} numberOfLines={1}>
          {song.artist}{song.year ? ` · ${song.year}` : ""}
        </Text>
        {!song.preview_url && (
          <Text style={styles.noPreview}>preview unavailable</Text>
        )}
      </View>
      <TouchableOpacity onPress={handleBookmark} style={styles.bookmarkBtn}>
        <Ionicons
          name={saved ? "bookmark" : "bookmark-outline"}
          size={24}
          color={saved ? "#3478F6" : "#888"}
        />
      </TouchableOpacity>
    </View>
  );
}

// A saved-song card.
export function SavedCard({ song, onRemove }) {
  return (
    <View style={styles.card}>
      {song.artwork_url ? (
        <Image source={{ uri: song.artwork_url }} style={styles.cardArtwork} />
      ) : (
        <View style={[styles.cardArtwork, styles.artworkPlaceholder]}>
          <Ionicons name="musical-note" size={18} color="#bbb" />
        </View>
      )}
      <View style={styles.rowText}>
        <Text style={styles.title} numberOfLines={1}>{song.title}</Text>
        <Text style={styles.sub} numberOfLines={1}>
          {song.artist}{song.year ? ` · ${song.year}` : ""}
        </Text>
      </View>
      <TouchableOpacity onPress={() => onRemove?.(song)} style={styles.bookmarkBtn}>
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
    paddingVertical: 10,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: "#ddd",
  },
  card: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    padding: 10,
    marginBottom: 10,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: "#ddd",
    borderRadius: 12,
  },
  artworkWrapper: {
    width: ARTWORK_SIZE,
    height: ARTWORK_SIZE,
    borderRadius: 8,
    overflow: "hidden",
  },
  artwork: {
    width: ARTWORK_SIZE,
    height: ARTWORK_SIZE,
    borderRadius: 8,
    backgroundColor: "#f0f0f0",
  },
  cardArtwork: {
    width: 44,
    height: 44,
    borderRadius: 6,
    backgroundColor: "#f0f0f0",
  },
  artworkPlaceholder: {
    alignItems: "center",
    justifyContent: "center",
  },
  playOverlay: {
    ...StyleSheet.absoluteFillObject,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(0,0,0,0.25)",
    borderRadius: 8,
  },
  rowText: { flex: 1 },
  title: { fontSize: 15, fontWeight: "500", color: "#111" },
  sub: { fontSize: 12, color: "#666", marginTop: 2 },
  noPreview: { fontSize: 11, color: "#aaa", fontStyle: "italic", marginTop: 2 },
  bookmarkBtn: { paddingLeft: 4 },
});
