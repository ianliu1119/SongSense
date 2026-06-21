import React, { useState } from "react";
import {
  View, Text, TextInput, TouchableOpacity, ScrollView,
  StyleSheet, ActivityIndicator, Alert,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { Audio } from "expo-av";
import { search, saveSong, unsaveSong, getSaved } from "../lib/api";
import { useAudioPlayer } from "../lib/useAudioPlayer";
import { ResultRow } from "../components/SongComponents";

export default function SearchScreen() {
  const insets = useSafeAreaInsets();
  const [genre, setGenre] = useState("");
  const [lyric, setLyric] = useState("");
  const [extra, setExtra] = useState("");
  const [recording, setRecording] = useState(null);
  const [audioUri, setAudioUri] = useState(null);
  const [results, setResults] = useState(null);
  const [savedIds, setSavedIds] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const { playingId, handlePlay } = useAudioPlayer();

  async function toggleRecord() {
    try {
      if (recording) {
        await recording.stopAndUnloadAsync();
        setAudioUri(recording.getURI());
        setRecording(null);
        return;
      }
      const perm = await Audio.requestPermissionsAsync();
      if (!perm.granted) return Alert.alert("Microphone permission needed");
      await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
      const { recording: rec } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(rec);
    } catch (e) {
      Alert.alert("Recording error", String(e));
    }
  }

  async function runSearch() {
    if (!genre.trim() && !lyric.trim() && !extra.trim() && !audioUri) {
      return Alert.alert("Add at least one clue", "Fill in a genre, lyric, extra info, or record a hum.");
    }
    setLoading(true);
    try {
      const [res, saved] = await Promise.all([
        search({ genre, lyric, extra, audioUri }),
        getSaved(),
      ]);
      setResults(res);
      setSavedIds(new Set(saved.map((s) => s.id)));
    } catch (e) {
      Alert.alert("Search failed", String(e));
    } finally {
      setLoading(false);
    }
  }

  const topPad = { paddingTop: insets.top + 20 };

  if (results) {
    return (
      <View style={[styles.container, topPad]}>
        <TouchableOpacity onPress={() => setResults(null)} style={styles.back}>
          <Ionicons name="arrow-back" size={18} color="#3478F6" />
          <Text style={styles.backText}>back</Text>
        </TouchableOpacity>
        <Text style={styles.heading}>Top 5 results</Text>
        <ScrollView>
          {results.map((s) => (
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
    <ScrollView
      style={styles.container}
      contentContainerStyle={[topPad, { paddingBottom: 40 }]}
    >
      <Text style={styles.pageTitle}>Find a Song</Text>
      <Field n="1" label="Sound">
        <TouchableOpacity style={styles.recordBtn} onPress={toggleRecord}>
          <Ionicons
            name={recording ? "stop-circle" : "mic-outline"}
            size={20}
            color={recording ? "#E24B4A" : "#3478F6"}
          />
          <Text style={styles.recordText}>
            {recording ? "Recording… tap to stop" : audioUri ? "Hum recorded ✓" : "Tap to hum / record"}
          </Text>
        </TouchableOpacity>
      </Field>

      <Field n="2" label="Genre">
        <TextInput
          style={styles.input}
          placeholder="ex. pop, rap, jazz…"
          placeholderTextColor="#999"
          value={genre}
          onChangeText={setGenre}
        />
      </Field>

      <Field n="3" label="Lyric">
        <TextInput
          style={[styles.input, styles.multiline]}
          placeholder="any lyrics you remember…"
          placeholderTextColor="#999"
          value={lyric}
          onChangeText={setLyric}
          multiline
        />
      </Field>

      <Field n="4" label="Extra info">
        <TextInput
          style={[styles.input, styles.multiline]}
          placeholder="mood, era, instruments, keywords…"
          placeholderTextColor="#999"
          value={extra}
          onChangeText={setExtra}
          multiline
        />
      </Field>

      <TouchableOpacity style={styles.goBtn} onPress={runSearch} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.goText}>Go!</Text>}
      </TouchableOpacity>
    </ScrollView>
  );
}

function Field({ n, label, children }) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>
        <Text style={{ color: "#3478F6" }}>{n}</Text>{"  "}{label}
      </Text>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingHorizontal: 16, backgroundColor: "#fff" },
  pageTitle: { fontSize: 26, fontWeight: "700", color: "#111", marginBottom: 20 },
  heading: { fontSize: 22, fontWeight: "700", color: "#111", marginBottom: 12 },
  field: { marginBottom: 16 },
  label: { fontSize: 13, fontWeight: "500", marginBottom: 6 },
  input: {
    borderWidth: StyleSheet.hairlineWidth, borderColor: "#bbb",
    borderRadius: 8, paddingHorizontal: 12, paddingVertical: 10, fontSize: 14,
  },
  multiline: { minHeight: 56, textAlignVertical: "top" },
  recordBtn: {
    flexDirection: "row", alignItems: "center", gap: 8,
    borderWidth: StyleSheet.hairlineWidth, borderColor: "#bbb",
    borderRadius: 8, padding: 12,
  },
  recordText: { fontSize: 13, color: "#555" },
  goBtn: {
    backgroundColor: "#3478F6", borderRadius: 10, padding: 14,
    alignItems: "center", marginTop: 8,
  },
  goText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  back: { flexDirection: "row", alignItems: "center", gap: 4, marginBottom: 8 },
  backText: { color: "#3478F6", fontSize: 14 },
});