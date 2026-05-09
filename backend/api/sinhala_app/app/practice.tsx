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
    const { sentenceId } = useLocalSearchParams();

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

    useEffect(() => {
        if (sentenceId && sentences.length > 0) {
            selectSentence(sentenceId as string);
        }
    }, [sentenceId, sentences.length, selectSentence]);

    const [mode, setMode] = useState<ScreenMode>('idle');
    const [currentWordIndex, setCurrentWordIndex] = useState(-1);
    const [karaokeWords, setKaraokeWords] = useState<KaraokeWord[]>([]);
    const [showFeedback, setShowFeedback] = useState(false);
    const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
    const [wordTimings, setWordTimings] = useState<WordTiming[]>([]);

    const audioUri = currentSentence?.hasAudio && currentSentence?.audioPath
        ? `${Config.API_BASE_URL}${currentSentence.audioPath}`
        : null;

    useEffect(() => {
        if (currentSentence) {
            setKaraokeWords(
                currentSentence.words.map(word => ({ text: word, status: 'pending' }))
            );

            let timings: WordTiming[] = [];

            if (currentSentence.timings && currentSentence.timings.length > 0) {
                timings = currentSentence.timings.map(t => ({
                    word: t.word,
                    startTime: t.start * 1000,
                    endTime: t.end * 1000
                }));
                console.log('Using backend timestamps for:', currentSentence.id);
            } else {
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

    useEffect(() => {
        if (audioRecorder.isRecording && !pronunciationFeedback.isConnected) {
            pronunciationFeedback.processAudioLevel(
                audioRecorder.metering,
                currentSentence?.words.length || 0
            );
        }
    }, [audioRecorder.metering, audioRecorder.isRecording, pronunciationFeedback.isConnected, currentSentence?.words.length, pronunciationFeedback]);

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

        if (audioRecorder.isRecording) {
            await audioRecorder.stopRecording();
            pronunciationFeedback.endSession();
        }

        setMode('playing');
        setCurrentWordIndex(-1);
        await audioPlayer.play();
    }, [audioPlayer, audioUri, isOnline, audioRecorder, pronunciationFeedback]);

    const handleRecord = useCallback(async () => {
        if (!currentSentence) return;

        if (audioRecorder.isRecording) {
            setMode('feedback');
            const uri = await audioRecorder.stopRecording();
            pronunciationFeedback.endSession();

            if (uri && currentSentence) {
                await pronunciationFeedback.analyzeAudio(uri, currentSentence.text);
            }
        } else {
            audioPlayer.stop(); 
            setMode('recording');
            setCurrentWordIndex(-1);
            setIsCorrect(null);
            setShowFeedback(false);

            setKaraokeWords(currentSentence.words.map(word => ({ text: word, status: 'pending' })));

            pronunciationFeedback.startSession(currentSentence.words.length);

            await audioRecorder.startRecording((base64) => {
                if (pronunciationFeedback.isConnected) {
                    pronunciationFeedback.analyzePartialAudio(base64, currentSentence.text);
                }
            });
        }
    }, [audioRecorder, pronunciationFeedback, currentSentence, audioPlayer]);

    useEffect(() => {
        if (pronunciationFeedback.finalScore && mode === 'feedback') {
            evaluatePronunciation();
        }
    }, [pronunciationFeedback.finalScore, mode]);

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

    const evaluatePronunciation = useCallback(() => {
        const finalScore = pronunciationFeedback.finalScore;

        if (finalScore) {
            const percentage = (finalScore.correctWords / finalScore.totalWords) * 100;
            setIsCorrect(percentage >= 70);
            setShowFeedback(true);

            setTimeout(() => {
                setShowFeedback(false);
                setMode('idle');
            }, 3000);
        }
    }, [pronunciationFeedback.finalScore]);

    useEffect(() => {
        if (!audioPlayer.isPlaying && !audioPlayer.isLoading && mode === 'playing') {
            setMode('idle');
            setCurrentWordIndex(-1);
        }
    }, [audioPlayer.isPlaying, audioPlayer.isLoading, mode]);

    const handleNextSentence = useCallback(() => {
        setMode('idle');
        setCurrentWordIndex(-1);
        setShowFeedback(false);
        setIsCorrect(null);
        nextSentence();
    }, [nextSentence]);

    const handlePreviousSentence = useCallback(() => {
        setMode('idle');
        setCurrentWordIndex(-1);
        setShowFeedback(false);
        setIsCorrect(null);
        previousSentence();
    }, [previousSentence]);

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
            {}
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

            {}
            {!isOnline && (
                <View style={styles.offlineWarning}>
                    <Ionicons name="cloud-offline-outline" size={20} color={Colors.warning} />
                    <Text style={styles.offlineText}>
                        Limited features in offline mode. Connect to internet for full experience.
                    </Text>
                </View>
            )}

            <ScrollView contentContainerStyle={styles.content}>
                {}
                <View style={styles.sentenceContainer}>
                    <KaraokeDisplay
                        words={karaokeWords}
                        currentWordIndex={currentWordIndex}
                        mode={mode === 'playing' ? 'playback' : (mode === 'recording' || mode === 'feedback') ? 'recording' : 'idle'}
                        fontSize={26}
                    />
                </View>

                {}
                {currentSentence.translation && (
                    <View style={styles.translationContainer}>
                        <Text style={styles.translationText}>{currentSentence.translation}</Text>
                    </View>
                )}

                {}
                <View style={styles.controlsContainer}>
                    <TouchableOpacity
                        style={[styles.controlButton, (!audioUri || mode !== 'idle') && styles.controlButtonDisabled]}
                        onPress={handlePlay}
                        disabled={!audioUri || mode !== 'idle'}
                    >
                        {}
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



                {}
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

                {}
            </ScrollView>

            {}
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
        alignItems: 'flex-start', 
        marginBottom: 24,
    },
    controlButton: {
        alignItems: 'center',
    },
    circleButton: {
        width: 70,
        height: 70,
        borderRadius: 40,
        backgroundColor: '#FFFFFF',
        alignItems: 'center',
        justifyContent: 'center',
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
        color: '#1EBF54', 
        fontWeight: '600',
        marginHorizontal: 4,
    },
    navButtonTextDisabled: {
        color: Colors.textSecondary,
    },
});
