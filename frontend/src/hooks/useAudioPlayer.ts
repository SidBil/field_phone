import { useCallback, useRef, useState } from "react";

interface AudioPlayerState {
  isPlaying: boolean;
  currentUrl: string | null;
  currentTime: number;
  duration: number;
}

/**
 * Hook for managing inline audio playback across the application.
 * Ensures only one token plays at a time — clicking a new play button
 * stops the previous one.
 */
export function useAudioPlayer() {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [state, setState] = useState<AudioPlayerState>({
    isPlaying: false,
    currentUrl: null,
    currentTime: 0,
    duration: 0,
  });

  const play = useCallback((url: string) => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
    const audio = new Audio(url);
    audioRef.current = audio;

    audio.addEventListener("timeupdate", () => {
      setState((prev) => ({ ...prev, currentTime: audio.currentTime }));
    });

    audio.addEventListener("loadedmetadata", () => {
      setState((prev) => ({ ...prev, duration: audio.duration }));
    });

    audio.addEventListener("ended", () => {
      setState((prev) => ({ ...prev, isPlaying: false, currentUrl: null }));
    });

    audio.play();
    setState({ isPlaying: true, currentUrl: url, currentTime: 0, duration: 0 });
  }, []);

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setState({ isPlaying: false, currentUrl: null, currentTime: 0, duration: 0 });
  }, []);

  const toggle = useCallback(
    (url: string) => {
      if (state.currentUrl === url && state.isPlaying) {
        stop();
      } else {
        play(url);
      }
    },
    [state.currentUrl, state.isPlaying, play, stop],
  );

  return { ...state, play, stop, toggle };
}
