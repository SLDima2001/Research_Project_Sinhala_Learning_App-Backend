import React from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { PronunciationStatus } from '../hooks/usePronunciationFeedback';
import { Colors } from '../constants/Colors';

export interface KaraokeWord {
    text: string;
    status: PronunciationStatus;
}

interface KaraokeDisplayProps {
    words: KaraokeWord[];
    currentWordIndex: number;
    mode: 'playback' | 'recording' | 'idle';
    fontSize?: number;
}

export const KaraokeDisplay: React.FC<KaraokeDisplayProps> = ({
    words,
    currentWordIndex,
    mode,
    fontSize = 32,
}) => {
    const getWordColor = (word: KaraokeWord, index: number): string => {
        // During playback, highlight current word in green (Duolingo style)
        if (mode === 'playback') {
            return index === currentWordIndex ? '#58CC02' : Colors.text;
        }

        // During/after recording, show feedback colors
        if (mode === 'recording') {
            switch (word.status) {
                case 'correct':
                    return Colors.correct;
                case 'incorrect':
                    return Colors.incorrect;
                case 'skipped':
                    return Colors.skipped;
                default:
                    return index === currentWordIndex ? '#58CC02' : Colors.text;
            }
        }

        // Idle mode - default text color
        return Colors.text;
    };

    const getWordScale = (index: number): number => {
        return index === currentWordIndex ? 1.1 : 1.0;
    };

    return (
        <View style={styles.container}>
            <View style={styles.wordsContainer}>
                {words.map((word, index) => {
                    const color = getWordColor(word, index);
                    const scale = getWordScale(index);
                    const isHighlighted = index === currentWordIndex;

                    return (
                        <View key={index} style={styles.wordWrapper}>
                            <Text
                                style={[
                                    styles.word,
                                    {
                                        color,
                                        fontSize,
                                        transform: [{ scale }],
                                        fontWeight: isHighlighted ? 'bold' : 'normal',
                                    },
                                ]}
                            >
                                {word.text}
                            </Text>
                        </View>
                    );
                })}
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        padding: 20,
        backgroundColor: Colors.surface,
        borderRadius: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 4,
    },
    wordsContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 12,
    },
    wordWrapper: {
        marginVertical: 8,
    },
    word: {
        fontFamily: 'System',
        lineHeight: 40,
        textAlign: 'center',
    },
});

export default KaraokeDisplay;
