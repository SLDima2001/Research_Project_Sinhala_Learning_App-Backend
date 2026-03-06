import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, Platform, Image } from 'react-native';
import { BlurView } from 'expo-blur';
import { Colors } from '../constants/Colors';
import ScoreDisplay from './ScoreDisplay';

interface FeedbackDisplayProps {
    isCorrect: boolean | null;
    message?: string;
    visible: boolean;
    score?: number;
    maxScore?: number;
}

export const FeedbackDisplay: React.FC<FeedbackDisplayProps> = ({
    isCorrect,
    message,
    visible,
    score,
    maxScore,
}) => {
    const scaleAnim = useRef(new Animated.Value(0)).current;
    const opacityAnim = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        if (visible) {
            // Entrance animation
            Animated.parallel([
                Animated.spring(scaleAnim, {
                    toValue: 1,
                    tension: 50,
                    friction: 7,
                    useNativeDriver: true,
                }),
                Animated.timing(opacityAnim, {
                    toValue: 1,
                    duration: 300,
                    useNativeDriver: true,
                }),
            ]).start();
        } else {
            // Exit animation
            Animated.parallel([
                Animated.timing(scaleAnim, {
                    toValue: 0,
                    duration: 200,
                    useNativeDriver: true,
                }),
                Animated.timing(opacityAnim, {
                    toValue: 0,
                    duration: 200,
                    useNativeDriver: true,
                }),
            ]).start();
        }
    }, [visible, scaleAnim, opacityAnim]);

    if (!visible) return null;


    const defaultMessage = isCorrect ? 'Excellent!' : 'Try Again!';

    // Colors
    const GREEN_COLOR = '#58CC02';
    const BROWN_COLOR = '#747250';

    // Glassy Styles based on correctness
    const headerColor = isCorrect ? 'rgba(88, 204, 2, 0.95)' : 'rgba(116, 114, 80, 0.95)';
    const containerBorderColor = isCorrect ? 'rgba(88, 204, 2, 0.5)' : 'rgba(116, 114, 80, 0.5)';
    const blurTint = isCorrect ? 'default' : 'dark'; // Use dark tint for brown for better contrast if needed, or 'default'
    // Actually, let's stick to a light/default tint but perhaps colored background for the body
    const bodyBgColor = isCorrect ? 'rgba(88, 204, 2, 0.1)' : 'rgba(116, 114, 80, 0.1)';

    return (
        <Animated.View
            style={[
                styles.container,
                {
                    opacity: opacityAnim,
                    transform: [{ scale: scaleAnim }],
                    borderColor: containerBorderColor,
                },
            ]}
        >
            <View style={styles.overflowContainer}>
                <BlurView intensity={80} tint="light" style={[styles.blurContainer, { backgroundColor: bodyBgColor }]}>
                    {/* Header Section */}
                    <View style={[styles.header, { backgroundColor: headerColor }]}>
                        <Image
                            source={isCorrect
                                ? require('../assets/images/feedback-excellent.png')
                                : require('../assets/images/feedback-tryagain.png')
                            }
                            style={styles.image}
                            resizeMode="contain"
                        />
                        <Text style={styles.headerText}>{message || defaultMessage}</Text>
                    </View>

                    {/* Body Section */}
                    <View style={styles.body}>
                        {(score !== undefined && maxScore !== undefined) && (
                            <View style={styles.scoreContainer}>
                                <ScoreDisplay
                                    score={score}
                                    maxScore={maxScore}
                                    showStars={true}
                                />
                            </View>
                        )}
                    </View>
                </BlurView>
            </View>
        </Animated.View>
    );
};

const styles = StyleSheet.create({
    container: {
        position: 'absolute',
        bottom: 50,
        alignSelf: 'center',
        zIndex: 1000,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.25,
        shadowRadius: 16,
        elevation: 10,
        borderRadius: 24,
        width: 320,
        borderWidth: 1.5,
    },
    overflowContainer: {
        borderRadius: 22, // Slightly less than container to fit inside border
        overflow: 'hidden',
    },
    blurContainer: {
        width: '100%',
        alignItems: 'center',
    },
    header: {
        width: '100%',
        paddingVertical: 18,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 12,
    },
    headerText: {
        fontSize: 26,
        fontWeight: 'bold',
        color: '#FFFFFF',
        textShadowColor: 'rgba(0,0,0,0.15)',
        textShadowOffset: { width: 0, height: 1 },
        textShadowRadius: 2,
    },
    image: {
        width: 60, // Slightly reduced to fit better linearly without making header too tall
        height: 60,
    },
    body: {
        width: '100%',
        padding: 20,
        alignItems: 'center',
    },
    scoreContainer: {
        width: '100%',
    },
});

export default FeedbackDisplay;
