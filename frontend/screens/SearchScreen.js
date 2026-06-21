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
import { C } from "../lib/theme";

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

  function reset() {
    setResults(null);
    setGenre("");
    setLyric("");
    setExtra("");
    setAudioUri(null);
  }

  const top = insets.top + 20;

  if (results) {
    return (
      <View style={[styles.container, { paddingTop: top }]}>
        <TouchableOpacity onPress={() => setResults(null)} style={styles.backRow}>
          <View style={styles.backBtn}>
            <Ionicons name="chevron-back" size={18} color={C.primary} />
          </View>
          <Text style={styles.backLabel}>New search</Text>
        </TouchableOpacity>
        <Text style={styles.resultsHeading}>Top results</Text>
        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 24 }}>
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
      contentContainerStyle={{ paddingTop: top, paddingBottom: 40 }}
      showsVerticalScrollIndicator={false}
      keyboardShouldPersistTaps="handled"
    >
      <Text style={styles.appName}>SongSense</Text>
      <Text style={styles.tagline}>What song is stuck in your head?</Text>

      <View style={styles.card}>
        <Field icon="mic-outline" label="Hum it">
          <TouchableOpacity
            style={[styles.recordBtn, recording && styles.recordBtnActive]}
            onPress={toggleRecord}
          >
            <Ionicons
              name={recording ? "stop-circle" : "mic"}
              size={20}
              color={recording ? C.danger : C.primary}
            />
            <Text style={[styles.recordText, recording && { color: C.danger }]}>
              {recording ? "Recording… tap to stop" : audioUri ? "Hum recorded ✓" : "Tap to record"}
            </Text>
            {recording && (
              <View style={styles.recordingDot} />
            )}
          </TouchableOpacity>
        </Field>

        <Field icon="musical-notes-outline" label="Genre">
          <TextInput
            style={styles.input}
            placeholder="pop, jazz, hip-hop…"
            placeholderTextColor={C.placeholder}
            value={genre}
            onChangeText={setGenre}
          />
        </Field>

        <Field icon="chatbubble-ellipses-outline" label="Lyrics">
          <TextInput
            style={[styles.input, styles.multiline]}
            placeholder="any lyrics you remember…"
            placeholderTextColor={C.placeholder}
            value={lyric}
            onChangeText={setLyric}
            multiline
          />
        </Field>

        <Field icon="options-outline" label="Vibe / Era / Instruments">
          <TextInput
            style={[styles.input, styles.multiline]}
            placeholder="sad, 80s, piano, female vocalist…"
            placeholderTextColor={C.placeholder}
            value={extra}
            onChangeText={setExtra}
            multiline
          />
        </Field>
      </View>

      <TouchableOpacity style={styles.goBtn} onPress={runSearch} disabled={loading} activeOpacity={0.85}>
        {loading
          ? <ActivityIndicator color="#fff" />
          : <>
              <Ionicons name="search" size={18} color="#fff" style={{ marginRight: 8 }} />
              <Text style={styles.goText}>Find Song</Text>
            </>
        }
      </TouchableOpacity>
    </ScrollView>
  );
}

function Field({ icon, label, children }) {
  return (
    <View style={styles.field}>
      <View style={styles.fieldHeader}>
        <Ionicons name={icon} size={14} color={C.primary} />
        <Text style={styles.fieldLabel}>{label}</Text>
      </View>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  container:       { flex: 1, backgroundColor: C.bg, paddingHorizontal: 20 },
  appName:         { fontSize: 30, fontWeight: "800", color: C.text, letterSpacing: -0.5 },
  tagline:         { fontSize: 15, color: C.sub, marginTop: 4, marginBottom: 24 },
  card:            { backgroundColor: C.card, borderRadius: 20, padding: 20, marginBottom: 16,
                     shadowColor: "#000", shadowOpacity: 0.06, shadowRadius: 12, shadowOffset: { width: 0, height: 4 },
                     elevation: 3 },
  field:           { marginBottom: 16 },
  fieldHeader:     { flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 8 },
  fieldLabel:      { fontSize: 12, fontWeight: "700", color: C.sub, textTransform: "uppercase", letterSpacing: 0.5 },
  input:           { backgroundColor: C.bg, borderRadius: 12, paddingHorizontal: 14,
                     paddingVertical: 12, fontSize: 15, color: C.text },
  multiline:       { minHeight: 60, textAlignVertical: "top" },
  recordBtn:       { flexDirection: "row", alignItems: "center", gap: 10, backgroundColor: C.bg,
                     borderRadius: 12, padding: 14 },
  recordBtnActive: { backgroundColor: "#FFF0F0" },
  recordText:      { fontSize: 14, color: C.sub, flex: 1 },
  recordingDot:    { width: 8, height: 8, borderRadius: 4, backgroundColor: C.danger },
  goBtn:           { backgroundColor: C.primary, borderRadius: 16, padding: 16,
                     flexDirection: "row", alignItems: "center", justifyContent: "center",
                     shadowColor: C.primary, shadowOpacity: 0.35, shadowRadius: 12, shadowOffset: { width: 0, height: 6 },
                     elevation: 4 },
  goText:          { color: "#fff", fontSize: 16, fontWeight: "700" },
  backRow:         { flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 20 },
  backBtn:         { width: 32, height: 32, borderRadius: 10, backgroundColor: C.primaryLight,
                     alignItems: "center", justifyContent: "center" },
  backLabel:       { fontSize: 15, color: C.primary, fontWeight: "600" },
  resultsHeading:  { fontSize: 26, fontWeight: "800", color: C.text, marginBottom: 16, letterSpacing: -0.5 },
});
