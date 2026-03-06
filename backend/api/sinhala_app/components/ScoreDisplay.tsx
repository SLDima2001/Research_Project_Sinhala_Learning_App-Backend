import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import {Colors} from '../constants/Colors';

interface ScoreDisplayProps {
    score: number;
    maxScore?: number;
    showStars?: boolean;
}

export const ScoreDisplay: React.FC<ScoreDisplayProps> = ({
    score,
    maxScore,
    showStars = true,
}) => {
    const scaleAnim = useRef(new Animated.Value(1)).current;
    const prevScore = useRef(score);

    // Animate when score changes
    useEffect(() => {
        if (score !== prevScore.current) {
            Animated.sequence([
                Animated.timing(scaleAnim, {
                    toValue: 1.3,
                    duration: 200,
                    useNativeDriver: true,
                }),
                Animated.timing(scaleAnim, {
                    toValue: 1,
                    duration: 200,
                    useNativeDriver: true,
                }),
            ]).start();
            prevScore.current = score;
        }
    }, [score, scaleAnim]);

    const getStars = (): string => {
        if (!maxScore) return '⭐';
        const percentage = (score / maxScore) * 100;
        if (percentage >= 90) return '⭐⭐⭐';
        if (percentage >= 70) return '⭐⭐';
        if (percentage >= 50) return '⭐';
        return '';
    };

    return (
        <View style={styles.container}>
            <Animated.View style={[styles.scoreContainer, { transform: [{ scale: scaleAnim }] }]}>
                <Text style={styles.scoreLabel}>Score</Text>
                <Text style={styles.scoreValue}>{score}</Text>
                {maxScore && <Text style={styles.maxScore}>/ {maxScore}</Text>}
            </Animated.View>
            {showStars && (
                <View style={styles.starsContainer}>
                    <Text style={styles.stars}>{getStars()}</Text>
                </View>
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        alignItems: 'center',
        padding: 16,
        backgroundColor: Colors.surface,
        borderRadius: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    scoreContainer: {
        flexDirection: 'row',
        alignItems: 'baseline',
        gap: 8,
    },
    scoreLabel: {
        fontSize: 16,
        fontWeight: '600',
        color: Colors.textSecondary,
    },
    scoreValue: {
        fontSize: 36,
        fontWeight: 'bold',
        color: Colors.primary,
    },
    maxScore: {
        fontSize: 20,
        fontWeight: '600',
        color: Colors.textSecondary,
    },
    starsContainer: {
        marginTop: 8,
    },
    stars: {
        fontSize: 24,
    },
});

export default ScoreDisplay;
