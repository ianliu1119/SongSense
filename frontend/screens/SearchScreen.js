import React, { useState } from "react";
import {
  View, Text, TextInput, TouchableOpacity, ScrollView,
  StyleSheet, ActivityIndicator, Alert,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Audio } from "expo-av";
import { search, saveSong } from "../lib/api";
import { ResultRow } from "../components/SongComponents";

export default function SearchScreen() {
  const [genre, setGenre] = useState("");
  const [lyric, setLyric] = useState("");
  const [extra, setExtra] = useState("");
  const [recording, setRecording] = useState(null);
  const [audioUri, setAudioUri] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

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
    setLoading(true);
    try {
      const res = await search({ genre, lyric, extra, audioUri });
      setResults(res);
    } catch (e) {
      Alert.alert("Search failed", String(e));
    } finally {
      setLoading(false);
    }
  }

  if (results) {
    return (
      <View style={styles.container}>
        <TouchableOpacity onPress={() => setResults(null)} style={styles.back}>
          <Ionicons name="arrow-back" size={18} color="#3478F6" />
          <Text style={styles.backText}>back</Text>
        </TouchableOpacity>
        <Text style={styles.heading}>Top 5 results</Text>
        <ScrollView>
          {results.map((s) => (
            <ResultRow key={s.id} song={s} onSave={(song) => saveSong(song.id)} />
          ))}
        </ScrollView>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>
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
        <TextInput style={styles.input} placeholder="ex. pop, rap, jazz…"
          value={genre} onChangeText={setGenre} />
      </Field>

      <Field n="3" label="Lyric">
        <TextInput style={[styles.input, styles.multiline]} placeholder="any lyrics you remember…"
          value={lyric} onChangeText={setLyric} multiline />
      </Field>

      <Field n="4" label="Extra info">
        <TextInput style={[styles.input, styles.multiline]} placeholder="mood, era, instruments, keywords…"
          value={extra} onChangeText={setExtra} multiline />
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
        <Text style={{ color: "#3478F6" }}>{n}</Text>  {label}
      </Text>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#fff" },
  heading: { fontSize: 18, fontWeight: "600", marginBottom: 8 },
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
