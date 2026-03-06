import React, { useEffect } from 'react';
import { StyleSheet, View, Dimensions } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withRepeat,
    withTiming,
    withSequence,
    withDelay,
    Easing,
    cancelAnimation
} from 'react-native-reanimated';

const { width, height } = Dimensions.get('window');

const BUBBLE_COUNT = 15;

const Bubble = ({ index }: { index: number }) => {
    const size = Math.random() * 40 + 20; // 20-60px
    const startX = Math.random() * width;
    const duration = Math.random() * 5000 + 5000; // 5-10s
    const delay = Math.random() * 5000;

    const translateY = useSharedValue(height + 100);
    const translateX = useSharedValue(startX);
    const opacity = useSharedValue(0.6);

    useEffect(() => {
        // Vertical movement
        translateY.value = withDelay(delay, withRepeat(
            withTiming(-100, { duration, easing: Easing.linear }),
            -1, // Infinite
            false
        ));

        // Horizontal squiggle
        translateX.value = withDelay(delay, withRepeat(
            withSequence(
                withTiming(startX + 30, { duration: duration / 2, easing: Easing.sin }),
                withTiming(startX - 30, { duration: duration / 2, easing: Easing.sin })
            ),
            -1,
            true
        ));

        // Opacity oscillation
        opacity.value = withDelay(delay, withRepeat(
            withSequence(
                withTiming(0.8, { duration: 2000 }),
                withTiming(0.4, { duration: 2000 })
            ),
            -1,
            true
        ));

        return () => {
            cancelAnimation(translateY);
            cancelAnimation(translateX);
            cancelAnimation(opacity);
        };
    }, []);

    const animatedStyle = useAnimatedStyle(() => {
        return {
            transform: [
                { translateY: translateY.value },
                { translateX: translateX.value }
            ],
            opacity: opacity.value
        };
    });

    return (
        <Animated.View
            style={[
                styles.bubble,
                {
                    width: size,
                    height: size,
                    borderRadius: size / 2,
                    backgroundColor: Math.random() > 0.5 ? 'rgba(255, 255, 255, 0.3)' : 'rgba(255, 200, 255, 0.3)',
                },
                animatedStyle
            ]}
        />
    );
};

export default function FairyBackground({ children }: { children?: React.ReactNode }) {
    return (
        <View style={styles.container}>
            <LinearGradient
                colors={['#E8F5E9', '#A5D6A7']} // Fresh Green Meadow
                style={StyleSheet.absoluteFill}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
            />

            {/* Overlay Gradient for more magic */}
            <LinearGradient
                colors={['hsla(0, 0%, 100%, 0.40)', 'transparent', 'rgba(160, 68, 255, 0.1)']}
                style={StyleSheet.absoluteFill}
            />

            {/* Bubbles */}
            {Array.from({ length: BUBBLE_COUNT }).map((_, i) => (
                <Bubble key={i} index={i} />
            ))}

            {/* Content */}
            <View style={styles.content}>
                {children}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    content: {
        flex: 1,
        zIndex: 1,
    },
    bubble: {
        position: 'absolute',
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.5)',
    }
});
