import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import Colors from '../constants/Colors';
import ScoreDisplay from '../components/ScoreDisplay';

export default function ResultsScreen() {
    const router = useRouter();
    const params = useLocalSearchParams();

    const score = parseInt(params.score as string) || 0;
    const maxScore = parseInt(params.maxScore as string) || 100;
    const correctWords = parseInt(params.correctWords as string) || 0;
    const totalWords = parseInt(params.totalWords as string) || 0;

    const percentage = (score / maxScore) * 100;
    const isExcellent = percentage >= 90;
    const isGood = percentage >= 70;

    const getMessage = () => {
        if (isExcellent) return 'Excellent Work! 🌟';
        if (isGood) return 'Great Job! 👏';
        return 'Keep Practicing! 💪';
    };

    const getEncouragement = () => {
        if (isExcellent) return 'You\'re a pronunciation master!';
        if (isGood) return 'You\'re doing really well!';
        return 'Practice makes perfect!';
    };

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView
                contentContainerStyle={styles.scrollContent}
                showsVerticalScrollIndicator={false}
            >
                {/* Main Message */}
                <View style={styles.messageContainer}>
                    <Text style={styles.messageTitle}>{getMessage()}</Text>
                    <Text style={styles.messageSubtitle}>{getEncouragement()}</Text>
                </View>

                {/* Score Display */}
                <View style={styles.scoreContainer}>
                    <ScoreDisplay score={score} maxScore={maxScore} showStars={true} />
                </View>

                {/* Detailed Stats */}
                <View style={styles.statsContainer}>
                    <Text style={styles.statsTitle}>Your Performance</Text>

                    <View style={styles.statRow}>
                        <Text style={styles.statLabel}>Correct Words:</Text>
                        <Text style={[styles.statValue, { color: Colors.success }]}>
                            {correctWords} / {totalWords}
                        </Text>
                    </View>

                    <View style={styles.statRow}>
                        <Text style={styles.statLabel}>Accuracy:</Text>
                        <Text style={[styles.statValue, { color: Colors.primary }]}>
                            {Math.round(percentage)}%
                        </Text>
                    </View>

                    {/* Progress Bar */}
                    <View style={styles.progressBarContainer}>
                        <View
                            style={[
                                styles.progressBar,
                                {
                                    width: `${percentage}%`,
                                    backgroundColor: isExcellent
                                        ? Colors.success
                                        : isGood
                                            ? Colors.primary
                                            : Colors.warning,
                                },
                            ]}
                        />
                    </View>
                </View>

                {/* Action Buttons */}
                <View style={styles.actionsContainer}>
                    <TouchableOpacity
                        style={[styles.button, styles.primaryButton]}
                        onPress={() => router.push('/')}
                    >
                        <Text style={styles.buttonText}>Practice Another</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                        style={[styles.button, styles.secondaryButton]}
                        onPress={() => router.back()}
                    >
                        <Text style={[styles.buttonText, { color: Colors.primary }]}>
                            Try Again
                        </Text>
                    </TouchableOpacity>
                </View>

                {/* Tips */}
                <View style={styles.tipsContainer}>
                    <Text style={styles.tipsTitle}>💡 Tips for Better Pronunciation:</Text>
                    <Text style={styles.tipText}>• Listen carefully to each word</Text>
                    <Text style={styles.tipText}>• Speak clearly and at a steady pace</Text>
                    <Text style={styles.tipText}>• Practice difficult words multiple times</Text>
                    <Text style={styles.tipText}>• Don't skip any words</Text>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.background,
    },
    scrollContent: {
        padding: 20,
        gap: 24,
    },
    messageContainer: {
        alignItems: 'center',
        marginTop: 20,
    },
    messageTitle: {
        fontSize: 32,
        fontWeight: 'bold',
        color: Colors.text,
        textAlign: 'center',
        marginBottom: 8,
    },
    messageSubtitle: {
        fontSize: 18,
        color: Colors.textSecondary,
        textAlign: 'center',
    },
    scoreContainer: {
        alignItems: 'center',
        marginVertical: 20,
    },
    statsContainer: {
        backgroundColor: Colors.surface,
        borderRadius: 16,
        padding: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 4,
    },
    statsTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: Colors.text,
        marginBottom: 16,
    },
    statRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
    statLabel: {
        fontSize: 16,
        color: Colors.textSecondary,
    },
    statValue: {
        fontSize: 20,
        fontWeight: 'bold',
    },
    progressBarContainer: {
        height: 12,
        backgroundColor: Colors.background,
        borderRadius: 6,
        marginTop: 16,
        overflow: 'hidden',
    },
    progressBar: {
        height: '100%',
        borderRadius: 6,
    },
    actionsContainer: {
        gap: 12,
    },
    button: {
        paddingVertical: 16,
        paddingHorizontal: 24,
        borderRadius: 12,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.2,
        shadowRadius: 4,
        elevation: 4,
    },
    primaryButton: {
        backgroundColor: Colors.primary,
    },
    secondaryButton: {
        backgroundColor: Colors.surface,
        borderWidth: 2,
        borderColor: Colors.primary,
    },
    buttonText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: Colors.textLight,
    },
    tipsContainer: {
        backgroundColor: Colors.surface,
        borderRadius: 16,
        padding: 20,
        borderLeftWidth: 4,
        borderLeftColor: Colors.info,
    },
    tipsTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: Colors.text,
        marginBottom: 12,
    },
    tipText: {
        fontSize: 16,
        color: Colors.text,
        lineHeight: 28,
        marginLeft: 8,
    },
});
