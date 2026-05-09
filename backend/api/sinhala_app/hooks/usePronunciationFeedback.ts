import { readAsStringAsync } from 'expo-file-system/legacy';
import * as FileSystem from 'expo-file-system'; 
import { useState, useCallback, useEffect, useRef } from 'react';
import { useWebSocket } from './useWebSocket';
import Config from '../constants/Config';

export type PronunciationStatus = 'correct' | 'incorrect' | 'skipped' | 'pending';

export interface WordFeedback {
    wordIndex: number;
    status: PronunciationStatus;
    timestamp: number;
}

export interface FinalScore {
    score: number;
    totalWords: number;
    correctWords: number;
    feedback: string;
}

export interface BackendFeedback {
    words: {
        word: string;
        status: 'green' | 'red' | 'gray';
        start?: number;
        end?: number;
        similarity?: number;
        spoken?: string;
    }[];
    all_correct: boolean;
    score: number;
}

export interface PronunciationFeedbackState {
    wordFeedbacks: Map<number, PronunciationStatus>;
    currentWordIndex: number;
    finalScore: FinalScore | null;
    isProcessing: boolean;
}

export const usePronunciationFeedback = (sentenceId: string | null) => {
    const { isConnected, sendMessage, onMessage, offMessage } = useWebSocket();

    const [state, setState] = useState<PronunciationFeedbackState>({
        wordFeedbacks: new Map(),
        currentWordIndex: -1,
        finalScore: null,
        isProcessing: false,
    });

    const simulationStateRef = useRef({
        lastUpdate: 0,
        wordIndex: 0,
        isActive: false
    });

    const handleWordFeedback = useCallback((data: WordFeedback) => {
        setState(prev => {
            const newFeedbacks = new Map(prev.wordFeedbacks);
            newFeedbacks.set(data.wordIndex, data.status);

            return {
                ...prev,
                wordFeedbacks: newFeedbacks,
                currentWordIndex: data.wordIndex,
            };
        });
    }, []);

    const handleFinalScore = useCallback((data: FinalScore) => {
        setState(prev => ({
            ...prev,
            finalScore: data,
            isProcessing: false,
        }));
    }, []);

    const handleFeedbackUiUpdate = useCallback((data: BackendFeedback, isPartial: boolean = false) => {
        console.log('Processing feedback update:', data, 'isPartial:', isPartial);
        setState(prev => {
            const newFeedbacks = new Map(prev.wordFeedbacks);

            data.words.forEach((item, index) => {
                let status: PronunciationStatus = 'pending';
                if (item.status === 'green') status = 'correct';
                else if (item.status === 'red') status = 'incorrect';
                else if (item.status === 'gray') {
                    if (isPartial) {
                        const lastRecognizedIndex = data.words.findLastIndex(w => w.status === 'green' || w.status === 'red');
                        if (index < lastRecognizedIndex) {
                            status = 'skipped'; 
                        } else {
                            status = 'pending'; 
                        }
                    } else {
                        status = 'skipped'; 
                    }
                }
                else if (item.status === 'pending') status = 'pending';

                newFeedbacks.set(index, status);
                console.log(`Word ${index} (${item.word}): ${item.status} -> ${status}`);
            });

            const finalScore: FinalScore | null = isPartial ? prev.finalScore : {
                score: data.score * Config.APP.POINTS_PER_CORRECT_WORD,
                totalWords: data.words.length,
                correctWords: data.score,
                feedback: data.all_correct ? 'Excellent!' : 'Keep practicing!',
            };

            const lastRecognizedIndex = data.words.findLastIndex(w => w.status === 'green' || w.status === 'red');

            return {
                ...prev,
                wordFeedbacks: newFeedbacks,
                currentWordIndex: isPartial ? lastRecognizedIndex : prev.currentWordIndex,
                finalScore,
                isProcessing: isPartial ? true : false, 
            };
        });
    }, []);

    const startSession = useCallback((totalWords: number = 0) => {
        if (!sentenceId) return;

        setState({
            wordFeedbacks: new Map(),
            currentWordIndex: -1,
            finalScore: null,
            isProcessing: true,
        });

        simulationStateRef.current = {
            lastUpdate: Date.now(),
            wordIndex: 0,
            isActive: true
        };

        if (isConnected) {
            sendMessage('start_recording', { sentenceId });
        } else {
            console.log('Starting simulated feedback session (Audio Driven)...');
        }
    }, [sentenceId, isConnected, sendMessage]);

    const processAudioLevel = useCallback((metering: number, totalWords: number) => {
        if (!simulationStateRef.current.isActive) return;

        if (metering > -50) {
            const now = Date.now();
            if (now - simulationStateRef.current.lastUpdate > 800) {
                const currentIndex = simulationStateRef.current.wordIndex;

                if (currentIndex >= totalWords) {
                    simulationStateRef.current.isActive = false;

                    if (!isConnected) {
                        endSession();
                        const correctCount = Math.floor(totalWords * 0.8);
                        handleFinalScore({
                            score: correctCount * Config.APP.POINTS_PER_CORRECT_WORD,
                            totalWords: totalWords,
                            correctWords: correctCount,
                            feedback: 'Great effort! (Offline Simulation)',
                        });
                    }
                    return;
                }

                let status: PronunciationStatus = 'pending';

                if (!isConnected) {
                    const isCorrect = Math.random() > 0.2;
                    status = isCorrect ? 'correct' : 'incorrect';
                }

                handleWordFeedback({
                    wordIndex: currentIndex,
                    status: status,
                    timestamp: now,
                });

                simulationStateRef.current.wordIndex++;
                simulationStateRef.current.lastUpdate = now;
            }
        }
    }, [isConnected, handleWordFeedback, handleFinalScore]);

    const analyzePartialAudio = useCallback((base64Audio: string, targetText: string) => {
        if (!isConnected) return;

        sendMessage('process_partial_audio', {
            audio: base64Audio,
            target: targetText
        });
    }, [isConnected, sendMessage]);

    const analyzeAudio = useCallback(async (audioUri: string, targetText: string) => {
        if (!isConnected) {
            return;
        }

        try {
            console.log('Reading audio file for backend analysis...');
            const base64Audio = await readAsStringAsync(audioUri, { encoding: 'base64' });

            console.log('Sending audio to backend...');
            sendMessage('process_voice', {
                audio: base64Audio,
                target: targetText
            });
        } catch (error) {
            console.error('Error sending audio to backend:', error);
            setState(prev => ({ ...prev, isProcessing: false }));
        }
    }, [isConnected, sendMessage]);

    const endSession = useCallback(() => {
        simulationStateRef.current.isActive = false;
        if (isConnected) {
            sendMessage('stop_recording');
        }
    }, [isConnected, sendMessage]);

    const getWordFeedback = useCallback((wordIndex: number): PronunciationStatus => {
        return state.wordFeedbacks.get(wordIndex) || 'pending';
    }, [state.wordFeedbacks]);

    const getCurrentScore = useCallback((): number => {
        let correctCount = 0;
        state.wordFeedbacks.forEach(status => {
            if (status === 'correct') correctCount++;
        });
        return correctCount * Config.APP.POINTS_PER_CORRECT_WORD;
    }, [state.wordFeedbacks]);

    const reset = useCallback(() => {
        simulationStateRef.current.isActive = false;
        setState({
            wordFeedbacks: new Map(),
            currentWordIndex: -1,
            finalScore: null,
            isProcessing: false,
        });
    }, []);

    useEffect(() => {
        onMessage('word_feedback', (data) => {
            console.log('Received word_feedback:', data);
            handleWordFeedback(data);
        });
        onMessage('final_score', (data) => {
            console.log('Received final_score:', data);
            handleFinalScore(data);
        });
        onMessage('feedback_ui_update', (data) => {
            console.log('Received feedback_ui_update (FINAL):', data);
            handleFeedbackUiUpdate(data, false); 
        });
        onMessage('partial_feedback_update', (data) => {
            console.log('Received partial_feedback_update:', data.words?.filter((w: any) => w.status === 'green' || w.status === 'red').length || 0, 'words recognized');
            handleFeedbackUiUpdate(data, true); 
        });

        return () => {
            offMessage('word_feedback');
            offMessage('final_score');
            offMessage('feedback_ui_update');
            offMessage('partial_feedback_update');
        };
    }, [onMessage, offMessage, handleWordFeedback, handleFinalScore, handleFeedbackUiUpdate]);

    return {
        ...state,
        startSession,
        analyzeAudio,
        analyzePartialAudio, 
        processAudioLevel,
        endSession,
        getWordFeedback,
        getCurrentScore,
        reset,
        isConnected,
    };
};

export default usePronunciationFeedback;
