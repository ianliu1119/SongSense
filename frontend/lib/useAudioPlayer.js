import { useState, useRef, useEffect } from "react";
import { Alert } from "react-native";
import { Audio } from "expo-av";

export function useAudioPlayer() {
  const [playingId, setPlayingId] = useState(null);
  const soundRef = useRef(null);

  useEffect(() => {
    return () => { soundRef.current?.unloadAsync(); };
  }, []);

  async function handlePlay(song) {
    if (!song.preview_url) {
      return Alert.alert("No preview", "No audio preview available for this song.");
    }
    if (playingId === song.id) {
      await soundRef.current?.stopAsync();
      await soundRef.current?.unloadAsync();
      soundRef.current = null;
      setPlayingId(null);
      return;
    }
    if (soundRef.current) {
      await soundRef.current.stopAsync();
      await soundRef.current.unloadAsync();
      soundRef.current = null;
    }
    try {
      await Audio.setAudioModeAsync({ allowsRecordingIOS: false, playsInSilentModeIOS: true });
      const { sound } = await Audio.Sound.createAsync(
        { uri: song.preview_url },
        { shouldPlay: true }
      );
      soundRef.current = sound;
      setPlayingId(song.id);
      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.didJustFinish) {
          sound.unloadAsync();
          soundRef.current = null;
          setPlayingId(null);
        }
      });
    } catch (e) {
      Alert.alert("Playback error", String(e));
      setPlayingId(null);
    }
  }

  return { playingId, handlePlay };
}
