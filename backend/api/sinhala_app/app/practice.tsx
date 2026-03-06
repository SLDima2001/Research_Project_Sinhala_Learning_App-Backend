import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../constants/Colors';
import Config from '../constants/Config';
import KaraokeDisplay, { KaraokeWord } from '../components/KarokeDisplay';
import RecordingButton from '../components/RecordingButton';
import FeedbackDisplay from '../components/FeedbackDisplay';
import ScoreDisplay from '../components/ScoreDisplay';
import { useAudioPlayer, WordTiming } from '../hooks/useAudioPlayer';
import { useAudioRecorder } from '../hooks/useAudioRecorder';
import { usePronunciationFeedback } from '../hooks/usePronunciationFeedback';
import { useSentences } from '../hooks/useSentences';

type ScreenMode = 'idle' | 'playing' | 'recording' | 'feedback';

export default function PracticeScreen() {
    const router = useRouter();
    // Get sentence ID from params
    const { sentenceId } = useLocalSearchParams();

    // Fetch sentences from backend (with offline fallback)
    const {
        currentSentence,
        isLoading: sentencesLoading,
        isOnline,
        error: sentencesError,
        nextSentence,
        previousSentence,
        selectSentence,
        currentIndex,
        sentences,
    } = useSentences(20);

    // Effect to select the correct sentence on load
    useEffect(() => {
        if (sentenceId && sentences.length > 0) {
            selectSentence(sentenceId as string);
        }
    }, [sentenceId, sentences.length, selectSentence]);

    // State
    const [mode, setMode] = useState<ScreenMode>('idle');
    const [currentWordIndex, setCurrentWordIndex] = useState(-1);
    const [karaokeWords, setKaraokeWords] = useState<KaraokeWord[]>([]);
    const [showFeedback, setShowFeedback] = useState(false);
    const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
    const [wordTimings, setWordTimings] = useState<WordTiming[]>([]);

    // Generate audio URL from backend
    const audioUri = currentSentence?.hasAudio && currentSentence?.audioPath
        ? `${Config.API_BASE_URL}${currentSentence.audioPath}`
        : null;

    // Initialize karaoke words when sentence changes
    useEffect(() => {
        if (currentSentence) {
            setKaraokeWords(
                currentSentence.words.map(word => ({ text: word, status: 'pending' }))
            );

            let timings: WordTiming[] = [];

            if (currentSentence.timings && currentSentence.timings.length > 0) {
                // Use backend timestamps (convert seconds to ms)
                timings = currentSentence.timings.map(t => ({
                    word: t.word,
                    startTime: t.start * 1000,
                    endTime: t.end * 1000
                }));
                console.log('Using backend timestamps for:', currentSentence.id);
            } else {
                // Fallback: Generate simple word timings
                timings = currentSentence.words.map((word, index) => ({
                    word,
                    startTime: index * 600,
                    endTime: (index + 1) * 600,
                }));
                console.log('Using heuristic timestamps for:', currentSentence.id);
            }

            setWordTimings(timings);
        }
    }, [currentSentence]);

    // Hooks
    const audioPlayer = useAudioPlayer(
        audioUri,
        wordTimings,
        (wordIndex) => {
            setCurrentWordIndex(wordIndex);
        },
        currentSentence?.text || ''
    );

    const audioRecorder = useAudioRecorder();

    const pronunciationFeedback = usePronunciationFeedback(currentSentence?.id || null);

    // Feed audio metering to simulation (offline mode only)
    useEffect(() => {
        if (audioRecorder.isRecording && !pronunciationFeedback.isConnected) {
            pronunciationFeedback.processAudioLevel(
                audioRecorder.metering,
                currentSentence?.words.length || 0
            );
        }
    }, [audioRecorder.metering, audioRecorder.isRecording, pronunciationFeedback.isConnected, currentSentence?.words.length, pronunciationFeedback]);

    // Handle play button
    const handlePlay = useCallback(async () => {
        if (!audioUri) {
            Alert.alert(
                'Audio Unavailable',
                isOnline
                    ? 'This sentence does not have audio available.'
                    : 'Audio playback requires internet connection.'
            );
            return;
        }

        // If recording, stop recording first
        if (audioRecorder.isRecording) {
            await audioRecorder.stopRecording();
            pronunciationFeedback.endSession();
        }

        setMode('playing');
        setCurrentWordIndex(-1);
        await audioPlayer.play();
    }, [audioPlayer, audioUri, isOnline, audioRecorder, pronunciationFeedback]);

    // Handle record button
    const handleRecord = useCallback(async () => {
        if (!currentSentence) return;

        if (audioRecorder.isRecording) {
            // Stop recording
            setMode('feedback');
            const uri = await audioRecorder.stopRecording();
            pronunciationFeedback.endSession();

            // Analyze with backend if connected
            if (uri && currentSentence) {
                await pronunciationFeedback.analyzeAudio(uri, currentSentence.text);
            }
        } else {
            // Start recording
            audioPlayer.stop(); // Stop playback if playing
            setMode('recording');
            setCurrentWordIndex(-1);
            setIsCorrect(null);
            setShowFeedback(false);

            // Reset word statuses
            setKaraokeWords(currentSentence.words.map(word => ({ text: word, status: 'pending' })));

            pronunciationFeedback.startSession(currentSentence.words.length);

            // Enable streaming if connected
            await audioRecorder.startRecording((base64) => {
                if (pronunciationFeedback.isConnected) {
                    pronunciationFeedback.analyzePartialAudio(base64, currentSentence.text);
                }
            });
        }
    }, [audioRecorder, pronunciationFeedback, currentSentence, audioPlayer]);

    // React to final score update
    useEffect(() => {
        if (pronunciationFeedback.finalScore && mode === 'feedback') {
            evaluatePronunciation();
        }
    }, [pronunciationFeedback.finalScore, mode]);

    // Update karaoke display based on pronunciation feedback
    useEffect(() => {
        if ((mode === 'recording' || mode === 'feedback') && currentSentence) {
            const updatedWords = currentSentence.words.map((word, index) => ({
                text: word,
                status: pronunciationFeedback.getWordFeedback(index),
            }));
            setKaraokeWords(updatedWords);
            setCurrentWordIndex(pronunciationFeedback.currentWordIndex);
        }
    }, [
        pronunciationFeedback.wordFeedbacks,
        pronunciationFeedback.currentWordIndex,
        pronunciationFeedback.getWordFeedback,
        mode,
        currentSentence,
    ]);

    // Evaluate pronunciation and show feedback
    const evaluatePronunciation = useCallback(() => {
        const finalScore = pronunciationFeedback.finalScore;

        if (finalScore) {
            const percentage = (finalScore.correctWords / finalScore.totalWords) * 100;
            setIsCorrect(percentage >= 70);
            setShowFeedback(true);

            // Hide feedback after 3 seconds
            setTimeout(() => {
                setShowFeedback(false);
                setMode('idle');
            }, 3000);
        }
    }, [pronunciationFeedback.finalScore]);

    // Handle audio player completion
    useEffect(() => {
        if (!audioPlayer.isPlaying && !audioPlayer.isLoading && mode === 'playing') {
            setMode('idle');
            setCurrentWordIndex(-1);
        }
    }, [audioPlayer.isPlaying, audioPlayer.isLoading, mode]);

    // Handle next sentence
    const handleNextSentence = useCallback(() => {
        setMode('idle');
        setCurrentWordIndex(-1);
        setShowFeedback(false);
        setIsCorrect(null);
        nextSentence();
    }, [nextSentence]);

    // Handle previous sentence
    const handlePreviousSentence = useCallback(() => {
        setMode('idle');
        setCurrentWordIndex(-1);
        setShowFeedback(false);
        setIsCorrect(null);
        previousSentence();
    }, [previousSentence]);

    // Loading state
    if (sentencesLoading) {
        return (
            <SafeAreaView style={styles.container}>
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color={Colors.primary} />
                    <Text style={styles.loadingText}>Loading sentences...</Text>
                </View>
            </SafeAreaView>
        );
    }

    // Error state
    if (!currentSentence) {
        return (
            <SafeAreaView style={styles.container}>
                <View style={styles.errorContainer}>
                    <Ionicons name="alert-circle-outline" size={64} color={Colors.error} />
                    <Text style={styles.errorText}>No sentences available</Text>
                    <Text style={styles.errorSubtext}>{sentencesError || 'Please try again later'}</Text>
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            {/* Header */}
            <View style={styles.header}>
                <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                    <Ionicons name="arrow-back" size={24} color={Colors.text} />
                </TouchableOpacity>
                <View style={styles.headerCenter}>
                    <Text style={styles.headerTitle}>Practice</Text>
                    <View style={styles.statusContainer}>
                        <View style={[styles.statusDot, { backgroundColor: isOnline ? Colors.correct : Colors.incorrect }]} />
                        <Text style={styles.statusText}>
                            {isOnline ? 'Online' : 'Offline'} • {currentIndex + 1}/{sentences.length}
                        </Text>
                    </View>
                </View>
                <View style={styles.placeholder} />
            </View>

            {/* Offline Mode Warning */}
            {!isOnline && (
                <View style={styles.offlineWarning}>
                    <Ionicons name="cloud-offline-outline" size={20} color={Colors.warning} />
                    <Text style={styles.offlineText}>
                        Limited features in offline mode. Connect to internet for full experience.
                    </Text>
                </View>
            )}

            <ScrollView contentContainerStyle={styles.content}>
                {/* Sentence Display */}
                <View style={styles.sentenceContainer}>
                    <KaraokeDisplay
                        words={karaokeWords}
                        currentWordIndex={currentWordIndex}
                        mode={mode === 'playing' ? 'playback' : (mode === 'recording' || mode === 'feedback') ? 'recording' : 'idle'}
                        fontSize={26}
                    />
                </View>

                {/* Translation (if available) */}
                {currentSentence.translation && (
                    <View style={styles.translationContainer}>
                        <Text style={styles.translationText}>{currentSentence.translation}</Text>
                    </View>
                )}

                {/* Control Buttons */}
                <View style={styles.controlsContainer}>
                    <TouchableOpacity
                        style={[styles.controlButton, (!audioUri || mode !== 'idle') && styles.controlButtonDisabled]}
                        onPress={handlePlay}
                        disabled={!audioUri || mode !== 'idle'}
                    >
                        {/* Circle Button Container */}
                        <View style={[styles.circleButton, { borderColor: '#1EBF54', borderWidth: 2 }]}>
                            <Ionicons name="play" size={40} color={'#1EBF54'} />
                        </View>
                        <Text style={[styles.controlButtonText, (!audioUri || mode !== 'idle') && styles.controlButtonTextDisabled]}>
                            Listen
                        </Text>
                    </TouchableOpacity>

                    <RecordingButton
                        isRecording={audioRecorder.isRecording}
                        onPress={handleRecord}
                        isDisabled={mode === 'playing' || mode === 'feedback'}
                    />
                </View>



                {/* Navigation Buttons */}
                <View style={styles.navigationContainer}>
                    <TouchableOpacity
                        style={[styles.navButton, currentIndex === 0 && styles.navButtonDisabled]}
                        onPress={handlePreviousSentence}
                        disabled={currentIndex === 0}
                    >
                        <Ionicons name="chevron-back" size={24} color={currentIndex === 0 ? Colors.textSecondary : '#1EBF54'} />
                        <Text style={[styles.navButtonText, currentIndex === 0 && styles.navButtonTextDisabled]}>
                            Previous
                        </Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                        style={[styles.navButton, currentIndex === sentences.length - 1 && styles.navButtonDisabled]}
                        onPress={handleNextSentence}
                        disabled={currentIndex === sentences.length - 1}
                    >
                        <Text style={[styles.navButtonText, currentIndex === sentences.length - 1 && styles.navButtonTextDisabled]}>
                            Next
                        </Text>
                        <Ionicons name="chevron-forward" size={24} color={currentIndex === sentences.length - 1 ? Colors.textSecondary : '#1EBF54'} />
                    </TouchableOpacity>
                </View>

                {/* Connection Status Removed */}
            </ScrollView>

            {/* Feedback Overlay */}
            {showFeedback && (
                <FeedbackDisplay
                    isCorrect={isCorrect ?? false}
                    message={isCorrect ? 'Excellent!' : 'Try Again!'}
                    visible={showFeedback}
                    score={pronunciationFeedback.finalScore?.correctWords}
                    maxScore={pronunciationFeedback.finalScore?.totalWords}
                />
            )}
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.background,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    loadingText: {
        marginTop: 16,
        fontSize: 16,
        color: Colors.textSecondary,
    },
    errorContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 24,
    },
    errorText: {
        marginTop: 16,
        fontSize: 20,
        fontWeight: 'bold',
        color: Colors.text,
    },
    errorSubtext: {
        marginTop: 8,
        fontSize: 14,
        color: Colors.textSecondary,
        textAlign: 'center',
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingHorizontal: 16,
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: Colors.border,
    },
    backButton: {
        padding: 8,
    },
    headerCenter: {
        flex: 1,
        alignItems: 'center',
    },
    headerTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: Colors.text,
    },
    statusContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 4,
    },
    statusDot: {
        width: 8,
        height: 8,
        borderRadius: 4,
        marginRight: 6,
    },
    statusText: {
        fontSize: 12,
        color: Colors.textSecondary,
    },
    placeholder: {
        width: 40,
    },
    offlineWarning: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: Colors.warningBackground,
        padding: 12,
        marginHorizontal: 16,
        marginTop: 8,
        borderRadius: 8,
    },
    offlineText: {
        flex: 1,
        marginLeft: 8,
        fontSize: 12,
        color: Colors.warning,
    },
    content: {
        padding: 24,
    },
    sentenceContainer: {
        minHeight: 200,
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 24,
    },
    translationContainer: {
        backgroundColor: Colors.surface,
        padding: 16,
        borderRadius: 12,
        marginBottom: 24,
    },
    translationText: {
        fontSize: 16,
        color: Colors.textSecondary,
        textAlign: 'center',
        fontStyle: 'italic',
    },
    controlsContainer: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        alignItems: 'flex-start', // Align to top so text aligns if buttons somehow differ
        marginBottom: 24,
    },
    controlButton: {
        alignItems: 'center',
        // padding: 16, // Layout is handled by container
    },
    circleButton: {
        width: 70,
        height: 70,
        borderRadius: 40,
        backgroundColor: '#FFFFFF',
        alignItems: 'center',
        justifyContent: 'center',
        // Shadow/Elevation removed to prevent artifacts
    },
    controlButtonDisabled: {
        opacity: 0.4,
    },
    controlButtonText: {
        marginTop: 8,
        fontSize: 14,
        color: Colors.text,
        fontWeight: '600',
    },
    controlButtonTextDisabled: {
        color: Colors.textSecondary,
    },
    navigationContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginTop: 24,
    },
    navButton: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 12,
        borderRadius: 8,
        backgroundColor: Colors.surface,
    },
    navButtonDisabled: {
        opacity: 0.4,
    },
    navButtonText: {
        fontSize: 16,
        color: '#1EBF54', // Green text
        fontWeight: '600',
        marginHorizontal: 4,
    },
    navButtonTextDisabled: {
        color: Colors.textSecondary,
    },
    // connectionStatus styles removed
});
