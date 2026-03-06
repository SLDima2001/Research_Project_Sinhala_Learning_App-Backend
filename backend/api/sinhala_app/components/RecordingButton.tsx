import React, { useEffect, useRef } from 'react';
import { TouchableOpacity, Text, StyleSheet, Animated, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../constants/Colors';

interface RecordingButtonProps {
    isRecording: boolean;
    isDisabled?: boolean;
    onPress: () => void;
}

export const RecordingButton: React.FC<RecordingButtonProps> = ({
    isRecording,
    isDisabled = false,
    onPress,
}) => {
    const pulseAnim = useRef(new Animated.Value(1)).current;
    const opacityAnim = useRef(new Animated.Value(1)).current;

    // Pulsing animation while recording
    useEffect(() => {
        if (isRecording) {
            Animated.loop(
                Animated.sequence([
                    Animated.timing(pulseAnim, {
                        toValue: 1.2,
                        duration: 800,
                        useNativeDriver: true,
                    }),
                    Animated.timing(pulseAnim, {
                        toValue: 1,
                        duration: 800,
                        useNativeDriver: true,
                    }),
                ])
            ).start();

            Animated.loop(
                Animated.sequence([
                    Animated.timing(opacityAnim, {
                        toValue: 0.6,
                        duration: 800,
                        useNativeDriver: true,
                    }),
                    Animated.timing(opacityAnim, {
                        toValue: 1,
                        duration: 800,
                        useNativeDriver: true,
                    }),
                ])
            ).start();
        } else {
            pulseAnim.setValue(1);
            opacityAnim.setValue(1);
        }
    }, [isRecording, pulseAnim, opacityAnim]);

    return (
        <TouchableOpacity
            onPress={onPress}
            disabled={isDisabled}
            activeOpacity={0.7}
            style={styles.container}
        >
            <Animated.View
                style={[
                    styles.button,
                    {
                        // Default to white background, or transparent if we want just the icon
                        // But user typically wants a button.
                        // Let's go with: White Background, Green Icon (standard clean look)
                        backgroundColor: '#FFFFFF',
                        transform: [{ scale: pulseAnim }],
                        opacity: isDisabled ? 0.5 : opacityAnim,
                        borderColor: isRecording ? Colors.error : '#1EBF54', // Green border or Red when recording
                        borderWidth: 2,
                    },
                ]}
            >
                <Ionicons
                    name={isRecording ? "mic" : "mic-outline"}
                    size={40}
                    color={isRecording ? Colors.error : '#1EBF54'} // Green icon
                />
            </Animated.View>
            <Text style={styles.label}>
                {isRecording ? 'Recording...' : 'Record'}
            </Text>
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    container: {
        alignItems: 'center',
        justifyContent: 'center',
    },
    button: {
        width: 70,
        height: 70,
        borderRadius: 40,
        alignItems: 'center',
        justifyContent: 'center',
        // Shadow/Elevation removed to prevent artifacts
    },
    // Removed innerCircle/innerSquare as we use Icon now
    label: {
        marginTop: 8,
        fontSize: 14, // Same as Listen button
        fontWeight: '600',
        color: Colors.text,
    },
});

export default RecordingButton;
