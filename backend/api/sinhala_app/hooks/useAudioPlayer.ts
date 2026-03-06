import { useState, useCallback, useRef, useEffect } from 'react';
import { Audio } from 'expo-av';
import { Sound } from 'expo-av/build/Audio';
import * as Speech from 'expo-speech';

export interface WordTiming {
    word: string;
    startTime: number;
    endTime: number;
}

export interface AudioPlayerState {
    isPlaying: boolean;
    isLoading: boolean;
    currentWordIndex: number;
    error: string | null;
}

export const useAudioPlayer = (
    audioUri: string | null,
    wordTimings: WordTiming[],
    onWordHighlight?: (wordIndex: number) => void,
    text?: string
) => {
    const [state, setState] = useState<AudioPlayerState>({
        isPlaying: false,
        isLoading: false,
        currentWordIndex: -1,
        error: null,
    });

    const soundRef = useRef<Sound | null>(null);
    const playbackIntervalRef = useRef<NodeJS.Timeout | null>(null);

    // Load audio
    const loadAudio = useCallback(async () => {
        if (!audioUri) return;

        try {
            setState(prev => ({ ...prev, isLoading: true, error: null }));

            // Unload previous sound
            if (soundRef.current) {
                await soundRef.current.unloadAsync();
            }

            // Configure audio mode
            await Audio.setAudioModeAsync({
                allowsRecordingIOS: false,
                playsInSilentModeIOS: true,
                staysActiveInBackground: false,
            });

            // Load new sound
            const { sound } = await Audio.Sound.createAsync(
                { uri: audioUri },
                {
                    shouldPlay: false,
                    progressUpdateIntervalMillis: 16 // MAX PRECISION (60fps)
                }
            );

            soundRef.current = sound;
            setState(prev => ({ ...prev, isLoading: false }));
        } catch (err: any) {
            console.error('Error loading audio:', err);
            setState(prev => ({ ...prev, isLoading: false, error: err.message }));
        }
    }, [audioUri]);

    const currentWordIndexRef = useRef<number>(-1);

    // Stop audio
    const stop = useCallback(async () => {
        try {
            if (audioUri && soundRef.current) {
                await soundRef.current.stopAsync();
                await soundRef.current.setPositionAsync(0);
            } else if (text) {
                await Speech.stop();
            }

            setState(prev => ({ ...prev, isPlaying: false, currentWordIndex: -1 }));

            if (playbackIntervalRef.current) {
                clearInterval(playbackIntervalRef.current);
                playbackIntervalRef.current = null;
            }
        } catch (err: any) {
            console.error('Error stopping audio:', err);
        }
    }, [audioUri, text]);

    // Play audio with word highlighting
    const play = useCallback(async () => {
        // If we have an audio URI but no sound loaded, try loading it
        if (audioUri && !soundRef.current) {
            await loadAudio();
        }

        try {
            setState(prev => ({ ...prev, isPlaying: true, currentWordIndex: -1 }));
            currentWordIndexRef.current = -1;

            if (audioUri && soundRef.current) {
                // Determine update interval (default is usually 500ms on Android, we need faster)
                // We'll set this when loading, but just in case
                await soundRef.current.setProgressUpdateIntervalAsync(16);

                // Setup status update listener based on ACTUAL playback position
                soundRef.current.setOnPlaybackStatusUpdate((status) => {
                    if (!status.isLoaded) return;

                    if (status.didJustFinish) {
                        stop();
                        return;
                    }

                    if (status.isPlaying) {
                        const currentTime = status.positionMillis;

                        // Find current word based on accurate playback time
                        const newIndex = wordTimings.findIndex(
                            (timing) => currentTime >= timing.startTime && currentTime < timing.endTime
                        );

                        // Debug logging (temporary)
                        // console.log(`Playback: ${currentTime}ms, Index: ${newIndex}`);

                        if (newIndex !== -1 && newIndex !== currentWordIndexRef.current) {
                            console.log(`Highlight change: ${currentWordIndexRef.current} -> ${newIndex} at ${currentTime}ms`);
                            currentWordIndexRef.current = newIndex;
                            setState(prev => ({ ...prev, currentWordIndex: newIndex }));
                            onWordHighlight?.(newIndex);
                        }
                    }
                });

                // Play recorded audio
                await soundRef.current.playAsync();

            } else if (text) {
                // Fallback for TTS (keep interval logic only for TTS)
                Speech.speak(text, {
                    language: 'si-LK',
                    onError: (e) => console.error('Speech error:', e)
                });

                const startTime = Date.now();
                playbackIntervalRef.current = setInterval(() => {
                    const currentTime = Date.now() - startTime;
                    const lastTiming = wordTimings[wordTimings.length - 1];

                    if (lastTiming && currentTime > lastTiming.endTime + 500) {
                        stop();
                        return;
                    }

                    const newIndex = wordTimings.findIndex(
                        (timing) => currentTime >= timing.startTime && currentTime < timing.endTime
                    );

                    if (newIndex !== -1 && newIndex !== currentWordIndexRef.current) {
                        currentWordIndexRef.current = newIndex;
                        setState(prev => ({ ...prev, currentWordIndex: newIndex }));
                        onWordHighlight?.(newIndex);
                    }
                }, 50) as unknown as NodeJS.Timeout;
            } else {
                console.warn('No audio URI or text provided for playback');
            }

        } catch (err: any) {
            console.error('Error playing audio:', err);
            setState(prev => ({ ...prev, isPlaying: false, error: err.message }));
        }
    }, [loadAudio, wordTimings, onWordHighlight, audioUri, text, stop]);

    // Pause audio
    const pause = useCallback(async () => {
        try {
            if (audioUri && soundRef.current) {
                await soundRef.current.pauseAsync();
            } else if (text) {
                await Speech.stop(); // TTS doesn't support pause well, so we stop
            }

            setState(prev => ({ ...prev, isPlaying: false }));

            if (playbackIntervalRef.current) {
                clearInterval(playbackIntervalRef.current);
                playbackIntervalRef.current = null;
            }
        } catch (err: any) {
            console.error('Error pausing audio:', err);
        }
    }, [audioUri, text]);



    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (soundRef.current) {
                soundRef.current.unloadAsync();
            }
            if (playbackIntervalRef.current) {
                clearInterval(playbackIntervalRef.current);
            }
            Speech.stop();
        };
    }, []);

    // Load audio when URI changes
    useEffect(() => {
        if (audioUri) {
            loadAudio();
        }
    }, [audioUri, loadAudio]);

    return {
        ...state,
        play,
        pause,
        stop,
        loadAudio,
    };
};

export default useAudioPlayer;
