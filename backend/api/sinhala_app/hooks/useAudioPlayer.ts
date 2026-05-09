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

    const loadAudio = useCallback(async () => {
        if (!audioUri) return;

        try {
            setState(prev => ({ ...prev, isLoading: true, error: null }));

            if (soundRef.current) {
                await soundRef.current.unloadAsync();
            }

            await Audio.setAudioModeAsync({
                allowsRecordingIOS: false,
                playsInSilentModeIOS: true,
                staysActiveInBackground: false,
            });

            const { sound } = await Audio.Sound.createAsync(
                { uri: audioUri },
                {
                    shouldPlay: false,
                    progressUpdateIntervalMillis: 16 
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

    const play = useCallback(async () => {
        if (audioUri && !soundRef.current) {
            await loadAudio();
        }

        try {
            setState(prev => ({ ...prev, isPlaying: true, currentWordIndex: -1 }));
            currentWordIndexRef.current = -1;

            if (audioUri && soundRef.current) {
                await soundRef.current.setProgressUpdateIntervalAsync(16);

                soundRef.current.setOnPlaybackStatusUpdate((status) => {
                    if (!status.isLoaded) return;

                    if (status.didJustFinish) {
                        stop();
                        return;
                    }

                    if (status.isPlaying) {
                        const currentTime = status.positionMillis;

                        const newIndex = wordTimings.findIndex(
                            (timing) => currentTime >= timing.startTime && currentTime < timing.endTime
                        );


                        if (newIndex !== -1 && newIndex !== currentWordIndexRef.current) {
                            console.log(`Highlight change: ${currentWordIndexRef.current} -> ${newIndex} at ${currentTime}ms`);
                            currentWordIndexRef.current = newIndex;
                            setState(prev => ({ ...prev, currentWordIndex: newIndex }));
                            onWordHighlight?.(newIndex);
                        }
                    }
                });

                await soundRef.current.playAsync();

            } else if (text) {
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

    const pause = useCallback(async () => {
        try {
            if (audioUri && soundRef.current) {
                await soundRef.current.pauseAsync();
            } else if (text) {
                await Speech.stop(); 
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
