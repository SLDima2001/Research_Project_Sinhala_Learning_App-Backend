import { useState, useCallback, useEffect, useRef } from 'react';
import { Audio } from 'expo-av';
import { readAsStringAsync } from 'expo-file-system/legacy';

export interface RecorderState {
    isRecording: boolean;
    isPaused: boolean;
    duration: number;
    metering: number;
    error: string | null;
}

// Global variable to track recording instance across re-renders/hot-reloads
let globalRecordingInstance: Audio.Recording | null = null;

export const useAudioRecorder = () => {
    const [state, setState] = useState<RecorderState>({
        isRecording: false,
        isPaused: false,
        duration: 0,
        metering: -160,
        error: null,
    });

    const streamIntervalRef = useRef<NodeJS.Timeout | null>(null);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (globalRecordingInstance) {
                // Determine if we should unload? 
                // Usually yes, if component unmounts we stop recording.
                cleanupRecording();
            }
        };
    }, []);

    const cleanupRecording = async () => {
        if (streamIntervalRef.current) {
            clearInterval(streamIntervalRef.current);
            streamIntervalRef.current = null;
        }

        if (globalRecordingInstance) {
            try {
                // Just try to unload directly. It might throw if already unloaded.
                await globalRecordingInstance.stopAndUnloadAsync();
            } catch (error) {
                // Ignore errors (e.g., if already unloaded)
            }
            globalRecordingInstance = null;
        }
    };

    const startRecording = useCallback(async (onStreamData?: (base64: string) => void) => {
        // Reset error state
        setState(prev => ({ ...prev, error: null }));

        try {
            // 1. Force cleanup of ANY existing global recording
            // This fixes the "Only one Recording object" error by finding the
            // orphan instance (from previous render) and killing it.
            if (globalRecordingInstance) {
                console.log('Found existing global recording, cleaning up...');
                await cleanupRecording();
            }

            console.log('Requesting permissions...');
            const { status } = await Audio.requestPermissionsAsync();
            if (status !== 'granted') {
                setState(prev => ({ ...prev, error: 'Permission to access microphone was denied' }));
                return;
            }

            await Audio.setAudioModeAsync({
                allowsRecordingIOS: true,
                playsInSilentModeIOS: true,
                staysActiveInBackground: true,
                shouldDuckAndroid: true,
                playThroughEarpieceAndroid: false,
            });

            console.log('Creating new recording...');
            const recording = new Audio.Recording();

            const options: Audio.RecordingOptions = {
                isMeteringEnabled: true,
                android: {
                    extension: '.wav',
                    outputFormat: Audio.AndroidOutputFormat.MPEG_4,
                    audioEncoder: Audio.AndroidAudioEncoder.AAC,
                    sampleRate: 16000,
                    numberOfChannels: 1,
                    bitRate: 64000,
                },
                ios: {
                    extension: '.wav',
                    outputFormat: Audio.IOSOutputFormat.LINEARPCM,
                    audioQuality: Audio.IOSAudioQuality.MAX,
                    sampleRate: 16000,
                    numberOfChannels: 1,
                    bitRate: 128000,
                    linearPCMBitDepth: 16,
                    linearPCMIsBigEndian: false,
                    linearPCMIsFloat: false,
                },
                web: {
                    mimeType: 'audio/webm',
                    bitsPerSecond: 64000,
                }
            };

            try {
                await recording.prepareToRecordAsync(options);

                recording.setOnRecordingStatusUpdate((status) => {
                    if (status.isRecording) {
                        setState(prev => ({
                            ...prev,
                            duration: status.durationMillis,
                            metering: status.metering ?? -160,
                        }));
                    }
                });

                await recording.startAsync();

                // Assign to global ASAP
                globalRecordingInstance = recording;

                // Start Streaming Interval if callback provided
                if (onStreamData) {
                    streamIntervalRef.current = setInterval(async () => {
                        try {
                            const uri = recording.getURI();
                            if (uri) {
                                // Read the latest file content
                                // Note: This reads the WHOLE file every time. 
                                // For files < 1MB (approx 30s of wav), this is performant enough for a prototype.
                                const base64 = await readAsStringAsync(uri, { encoding: 'base64' });
                                onStreamData(base64);
                            }
                        } catch (e) {
                            console.error('Streaming read error:', e);
                        }
                    }, 500) as unknown as NodeJS.Timeout; // Optimized for real-time feedback
                }

                setState(prev => ({
                    ...prev,
                    isRecording: true,
                    isPaused: false,
                    duration: 0,
                    error: null
                }));

            } catch (setupError) {
                console.error('Recording setup failed:', setupError);
                // Clean up the local instance immediately if setup failed
                try {
                    await recording.stopAndUnloadAsync();
                } catch (e) { }
                globalRecordingInstance = null;
                throw setupError;
            }

        } catch (err: any) {
            console.error('Failed to start recording:', err);
            setState(prev => ({ ...prev, error: err.message }));
        }
    }, []);

    const stopRecording = useCallback(async () => {
        // Clear streaming interval
        if (streamIntervalRef.current) {
            clearInterval(streamIntervalRef.current);
            streamIntervalRef.current = null;
        }

        if (!globalRecordingInstance) return null;

        try {
            console.log('Stopping recording...');
            await globalRecordingInstance.stopAndUnloadAsync();
            const uri = globalRecordingInstance.getURI();

            globalRecordingInstance = null;
            setState(prev => ({ ...prev, isRecording: false, isPaused: false, metering: -160 }));

            console.log('Recording stopped, URI:', uri);
            return uri;
        } catch (err: any) {
            console.error('Failed to stop recording', err);
            setState(prev => ({ ...prev, error: err.message }));
            return null;
        }
    }, []);

    const togglePause = useCallback(async () => {
        if (!globalRecordingInstance) return;

        try {
            if (state.isPaused) {
                await globalRecordingInstance.startAsync();
                setState(prev => ({ ...prev, isPaused: false }));
            } else {
                await globalRecordingInstance.pauseAsync();
                setState(prev => ({ ...prev, isPaused: true }));
            }
        } catch (err: any) {
            setState(prev => ({ ...prev, error: err.message }));
        }
    }, [state.isPaused]);

    return {
        ...state,
        startRecording,
        stopRecording,
        togglePause,
    };
};
