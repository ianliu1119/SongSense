import React, { useState } from "react";
import { View, Text, TouchableOpacity, Image, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { C } from "../lib/theme";

const ART = 60;

function Artwork({ uri, canPlay, playing, onPress }) {
  return (
    <TouchableOpacity onPress={onPress} disabled={!canPlay} activeOpacity={0.85} style={styles.artWrap}>
      {uri ? (
        <Image source={{ uri }} style={styles.art} />
      ) : (
        <View style={[styles.art, styles.artFallback]}>
          <Ionicons name="musical-note" size={24} color={C.border} />
        </View>
      )}
      <View style={[styles.playOverlay, !canPlay && styles.playOverlayDimmed]}>
        <Ionicons
          name={playing ? "pause" : "play"}
          size={20}
          color="#fff"
        />
      </View>
    </TouchableOpacity>
  );
}

export function ResultRow({ song, onSave, onUnsave, onPlay, playing, initialSaved }) {
  const [saved, setSaved] = useState(initialSaved ?? false);

  function handleBookmark() {
    const next = !saved;
    setSaved(next);
    if (next) onSave?.(song);
    else onUnsave?.(song);
  }

  return (
    <View style={styles.row}>
      <Artwork
        uri={song.artwork_url}
        canPlay={!!song.preview_url}
        playing={playing}
        onPress={() => onPlay?.(song)}
      />
      <View style={styles.info}>
        <Text style={styles.title} numberOfLines={1}>{song.title}</Text>
        <Text style={styles.sub} numberOfLines={1}>
          {song.artist}{song.year ? ` · ${song.year}` : ""}
        </Text>
        {!song.preview_url && (
          <Text style={styles.noPreview}>No preview available</Text>
        )}
      </View>
      <TouchableOpacity onPress={handleBookmark} style={styles.bookmarkBtn} hitSlop={8}>
        <Ionicons
          name={saved ? "bookmark" : "bookmark-outline"}
          size={22}
          color={saved ? C.primary : C.sub}
        />
      </TouchableOpacity>
    </View>
  );
}

export function SavedCard({ song, onRemove }) {
  return (
    <View style={styles.card}>
      {song.artwork_url ? (
        <Image source={{ uri: song.artwork_url }} style={styles.cardArt} />
      ) : (
        <View style={[styles.cardArt, styles.artFallback]}>
          <Ionicons name="musical-note" size={18} color={C.border} />
        </View>
      )}
      <View style={styles.info}>
        <Text style={styles.title} numberOfLines={1}>{song.title}</Text>
        <Text style={styles.sub} numberOfLines={1}>
          {song.artist}{song.year ? ` · ${song.year}` : ""}
        </Text>
      </View>
      <TouchableOpacity onPress={() => onRemove?.(song)} style={styles.bookmarkBtn} hitSlop={8}>
        <Ionicons name="bookmark" size={20} color={C.primary} />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  // Result row
  row: {
    flexDirection: "row", alignItems: "center", gap: 14,
    backgroundColor: C.card, borderRadius: 16, padding: 12, marginBottom: 10,
    shadowColor: "#000", shadowOpacity: 0.05, shadowRadius: 8, shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  artWrap: { width: ART, height: ART, borderRadius: 12, overflow: "hidden" },
  art:     { width: ART, height: ART, borderRadius: 12, backgroundColor: C.bg },
  artFallback: { alignItems: "center", justifyContent: "center" },
  playOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0.32)",
    alignItems: "center", justifyContent: "center",
  },
  playOverlayDimmed: { backgroundColor: "rgba(0,0,0,0.15)" },
  info:        { flex: 1 },
  title:       { fontSize: 15, fontWeight: "700", color: C.text },
  sub:         { fontSize: 12, color: C.sub, marginTop: 3 },
  noPreview:   { fontSize: 11, color: C.placeholder, marginTop: 3, fontStyle: "italic" },
  bookmarkBtn: { padding: 4 },

  // Saved card
  card: {
    flexDirection: "row", alignItems: "center", gap: 14,
    backgroundColor: C.card, borderRadius: 16, padding: 12, marginBottom: 10,
    shadowColor: "#000", shadowOpacity: 0.05, shadowRadius: 8, shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  cardArt: { width: 48, height: 48, borderRadius: 10, backgroundColor: C.bg },
});
