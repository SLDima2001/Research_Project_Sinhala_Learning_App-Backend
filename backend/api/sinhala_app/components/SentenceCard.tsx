import React from 'react';
import { TouchableOpacity, Text, StyleSheet, View } from 'react-native';
import { Colors } from '../constants/Colors';

export interface Sentence {
    id: string;
    text: string;
    difficulty?: string;
    completed?: boolean;
}

interface SentenceCardProps {
    sentence: Sentence;
    onPress: () => void;
}

export const SentenceCard: React.FC<SentenceCardProps> = ({ sentence, onPress }) => {
    const getDifficultyColor = (): string => {
        switch (sentence.difficulty) {
            case 'easy':
                return Colors.success;
            case 'medium':
                return Colors.warning;
            case 'hard':
                return Colors.error;
            case 'offline':
                return Colors.success;
            default:
                return Colors.textSecondary;
        }
    };

    const getDifficultyLabel = (): string => {
        if (!sentence.difficulty) return 'Unknown';
        return sentence.difficulty.charAt(0).toUpperCase() + sentence.difficulty.slice(1);
    };

    return (
        <TouchableOpacity
            style={[styles.container, sentence.completed && styles.completed]}
            onPress={onPress}
            activeOpacity={0.7}
        >
            <View style={styles.content}>
                <Text style={styles.text} numberOfLines={2}>
                    {sentence.text}
                </Text>
                <View style={styles.footer}>
                    <View style={[styles.difficultyBadge, { backgroundColor: getDifficultyColor() }]}>
                        <Text style={styles.difficultyText}>{getDifficultyLabel()}</Text>
                    </View>
                    {sentence.completed && (
                        <Text style={styles.completedIcon}>✓</Text>
                    )}
                </View>
            </View>
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    container: {
        backgroundColor: Colors.surface,
        borderRadius: 16,
        padding: 20,
        marginVertical: 8,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 4,
        borderWidth: 2,
        borderColor: 'transparent',
    },
    completed: {
        borderColor: Colors.success,
        opacity: 0.8,
    },
    content: {
        gap: 12,
    },
    text: {
        fontSize: 20,
        fontWeight: '600',
        color: Colors.text,
        lineHeight: 28,
    },
    footer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    difficultyBadge: {
        paddingHorizontal: 12,
        paddingVertical: 4,
        borderRadius: 12,
    },
    difficultyText: {
        fontSize: 12,
        fontWeight: '700',
        color: Colors.textLight,
        textTransform: 'uppercase',
    },
    completedIcon: {
        fontSize: 24,
        color: Colors.success,
    },
});

export default SentenceCard;
