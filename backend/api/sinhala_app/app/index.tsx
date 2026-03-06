import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, BackHandler, useWindowDimensions, ActivityIndicator, Image } from 'react-native';
import { useRouter } from 'expo-router';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withSequence,
    withSpring,
    withTiming,
    useDerivedValue,
    interpolate,
    Extrapolate,
    withRepeat
} from 'react-native-reanimated';
import { Audio } from 'expo-av';
import { TouchableWithoutFeedback } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import Colors from '../constants/Colors';
import SentenceCard, { Sentence } from '../components/SentenceCard';
import { useSentences } from '../hooks/useSentences';
import { useWebSocket } from '../hooks/useWebSocket';
import FairyBackground from '../components/FairyBackground';
import GameLevelButton from '../components/GameLevelButton';


type CategoryType = 'offline' | 'easy' | 'medium' | 'hard';

const LoadingChicken = () => {
    const transY = useSharedValue(0);
    const [sound, setSound] = useState<Audio.Sound | null>(null);

    React.useEffect(() => {
        // Animation
        transY.value = withRepeat(
            withTiming(-20, { duration: 600 }), // Increased movement for larger image
            -1,
            true
        );

        // Sound
        const playSound = async () => {
            try {
                // Try to load the sound - user needs to add 'loading_sound.mp3' to assets/sounds/
                // If it doesn't exist, this will safely fail without crashing
                const { sound: playbackObject } = await Audio.Sound.createAsync(
                    require('../assets/sounds/loading_sound.mp3'),
                    { shouldPlay: true, isLooping: true }
                );
                setSound(playbackObject);
            } catch (error) {
                console.log('Error loading sound (file might be missing):', error);
            }
        };

        playSound();

        return () => {
            if (sound) {
                sound.unloadAsync();
            }
        };
    }, []);

    // Cleanup sound when unmounting if it was set later
    React.useEffect(() => {
        return () => {
            if (sound) {
                sound.unloadAsync();
            }
        };
    }, [sound]);

    const style = useAnimatedStyle(() => ({
        transform: [{ translateY: transY.value }]
    }));

    return (
        <Animated.Image
            source={require('../assets/images/success_chicken.png')}
            style={[{ width: 500, height: 500, resizeMode: 'contain', marginBottom: 30 }, style]}
        />
    );
};

export default function HomeScreen() {
    const router = useRouter();
    const { isConnected } = useWebSocket();
    const [selectedCategory, setSelectedCategory] = useState<CategoryType | null>(null);
    const scrollViewRef = React.useRef<ScrollView>(null);

    const { sentences, isLoading, refetch: fetchByCategory } = useSentences();

    // ... (Keep existing handlers)
    const handleCategoryPress = (category: CategoryType) => {
        setSelectedCategory(category);
        fetchByCategory(category, 40);
    };

    const handleBackToCategories = () => {
        setSelectedCategory(null);
    };

    const handleSentencePress = (sentence: Sentence) => {
        router.push({
            pathname: '/practice',
            params: { sentenceId: sentence.id },
        });
    };

    // Scroll to bottom when category is selected and sentences loaded
    React.useEffect(() => {
        if (selectedCategory && sentences.length > 0) {
            // Slight delay to ensure layout is ready
            setTimeout(() => {
                scrollViewRef.current?.scrollToEnd({ animated: false });
            }, 100);
        }
    }, [selectedCategory, sentences]);

    const getCategoryLabel = (cat: string) => {
        if (cat === 'offline') return 'Offline Practice';
        return `${cat.charAt(0).toUpperCase() + cat.slice(1)} Level`;
    };

    const getCategoryIcon = (cat: string) => {
        switch (cat) {
            case 'offline': return 'cloud-offline-outline';
            case 'easy': return 'calendar-outline';
            case 'medium': return 'bar-chart-outline';
            case 'hard': return 'trophy-outline';
            default: return 'list-outline';
        }
    };

    // Handle hardware back button when in sentence list view
    React.useEffect(() => {
        const backAction = () => {
            if (selectedCategory) {
                setSelectedCategory(null);
                return true;
            }
            return false;
        };

        const backHandler = BackHandler.addEventListener(
            'hardwareBackPress',
            backAction
        );

        return () => backHandler.remove();
    }, [selectedCategory]);

    const renderCategoryButtons = () => (
        <View style={styles.categoriesContainer}>
            {(['offline', 'easy', 'medium', 'hard'] as CategoryType[]).map((cat) => (
                <TouchableOpacity
                    key={cat}
                    style={[
                        styles.categoryButton,
                        { borderColor: cat === 'offline' ? Colors.success : Colors.border }
                    ]}
                    onPress={() => handleCategoryPress(cat)}
                >
                    <Ionicons
                        name={getCategoryIcon(cat) as any}
                        size={32}
                        color={Colors.success}
                        style={{ marginBottom: 8 }}
                    />
                    <Text style={styles.categoryButtonText}>
                        {cat === 'offline' ? 'Offline' : cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </Text>
                    <Text style={styles.categorySubtext}>
                        {cat === 'offline' ? 'Practice without internet' : `Practice ${cat} sentences`}
                    </Text>
                </TouchableOpacity>
            ))}
        </View>
    );

    // Game Path Configuration
    const { width: SCREEN_WIDTH } = useWindowDimensions();
    const BUTTON_SIZE = 60;
    const VERTICAL_SPACING = 110; // Spacing for vertical layout

    const renderSentenceList = () => {
        if (isLoading) {
            return (
                <View style={styles.centerContainer}>
                    <LoadingChicken />
                    <Text style={styles.loadingText}>Loading levels...</Text>
                </View>
            );
        }

        if (!sentences || sentences.length === 0) {
            return (
                <View style={styles.centerContainer}>
                    <Text style={styles.emptyText}>No levels found for {selectedCategory}</Text>
                </View>
            );
        }

        const containerWidth = SCREEN_WIDTH;
        const centerOffset = containerWidth / 2;

        // Perspective Configuration
        const BASE_AMPLITUDE = containerWidth * 0.35; // Wide at bottom
        const MIN_AMPLITUDE = containerWidth * 0.1;   // Narrow at top
        const START_SCALE = 1.1; // Larger at bottom
        const END_SCALE = 0.6;   // Smaller at top

        // Layout Spacing
        const BOTTOM_PADDING = 150; // Start point padding
        const TOP_PADDING = 100;    // End point padding

        const containerHeight = (sentences.length * VERTICAL_SPACING) + BOTTOM_PADDING + TOP_PADDING;

        // Generate Path Data from BOTTOM up
        // Index 0 (Level 1) is at the BOTTOM
        const points = sentences.map((_, index) => {
            // 1. Calculate Progress (0 = Bottom/Start, 1 = Top/End)
            const progress = index / Math.max(sentences.length - 1, 1);

            // 2. Determine Y Position (Inverted)
            // Level 1 at Bottom
            const y = containerHeight - BOTTOM_PADDING - (index * VERTICAL_SPACING);

            // 3. Determine Perspective Factors
            const currentAmplitude = BASE_AMPLITUDE * (1 - (progress * 0.6));
            const currentScale = START_SCALE - (progress * (START_SCALE - END_SCALE));

            // 4. Calculate X Position
            const x = centerOffset + Math.sin(index * 0.6) * currentAmplitude;

            return { x, y, scale: currentScale };
        });



        return (
            <View style={{ height: containerHeight, position: 'relative' }}>
                

                {/* Buttons Layer */}
                {sentences.map((sentence, index) => {
                    const isCompleted = sentence.completed;
                    const { x: left, y: top, scale } = points[index];

                    // Unlock all buttons as per user request
                    const displayStatus = isCompleted ? 'completed' : 'current';

                    return (
                        <GameLevelButton
                            key={sentence.id}
                            level={index + 1}
                            status={displayStatus}
                            onPress={() => handleSentencePress(sentence)}
                            style={{
                                position: 'absolute',
                                left: left - (BUTTON_SIZE / 2),
                                top: top - (BUTTON_SIZE / 2),
                                transform: [{ scale: scale }] // Apply perspective scale
                            }}
                        />
                    );
                })}
            </View>
        );
    };

    return (
        <FairyBackground>
            <SafeAreaView style={styles.container}>
                {selectedCategory && (
                    <View style={{
                        position: 'absolute',
                        top: 20,
                        left: 20,
                        zIndex: 100
                    }}>
                        <TouchableOpacity
                            onPress={handleBackToCategories}
                            style={{
                                backgroundColor: '#FFFFFF',
                                borderRadius: 30,
                                padding: 8,
                                shadowColor: "#000",
                                shadowOffset: {
                                    width: 0,
                                    height: 2,
                                },
                                shadowOpacity: 0.25,
                                shadowRadius: 3.84,
                                elevation: 5,
                                width: 50,
                                height: 50,
                                alignItems: 'center',
                                justifyContent: 'center',
                            }}
                        >
                            <Ionicons name="chevron-back" size={30} color="#58CC02" />
                        </TouchableOpacity>
                    </View>
                )}

                <ScrollView
                    ref={scrollViewRef}
                    contentContainerStyle={styles.scrollContent}
                    showsVerticalScrollIndicator={false}
                >
                    {/* Header */}
                    {/* Header */}
                    {!selectedCategory && (
                        <View style={styles.header}>
                            <Text style={styles.title}>Welcome! 🎓</Text>
                            <Text style={styles.subtitle}>
                                Choose a mode to start practicing
                            </Text>
                            <View style={styles.statusContainer}>
                                <View
                                    style={[
                                        styles.statusDot,
                                        { backgroundColor: isConnected ? Colors.success : Colors.error },
                                    ]}
                                />
                                <Text style={styles.statusText}>
                                    {isConnected ? 'Online' : 'Offline Mode'}
                                </Text>
                            </View>
                        </View>
                    )}

                    {/* Main Content */}
                    {selectedCategory ? renderSentenceList() : renderCategoryButtons()}

                </ScrollView>
            </SafeAreaView>
        </FairyBackground>
    );
}

const styles = StyleSheet.create({
    headerRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 24,
        paddingHorizontal: 4,
    },
    headerRight: {
        alignItems: 'flex-end',
    },
    greenDot: {
        width: 12,
        height: 12,
        borderRadius: 6,
        backgroundColor: Colors.success,
        marginBottom: 4,
    },
    levelText: {
        fontSize: 16,
        color: Colors.text,
        fontWeight: '500',
    },
    navButton: {
        padding: 4,
    },
    container: {
        flex: 1,
        // backgroundColor: Colors.background, // Removed for FairyBackground
    },
    scrollContent: {
        flexGrow: 1,
        paddingHorizontal: 20,
        paddingBottom: 20,
        paddingTop: 8,
    },
    header: {
        marginBottom: 32,
        alignItems: 'center',
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
        color: Colors.text,
        marginBottom: 8,
        textAlign: 'center',
    },
    subtitle: {
        fontSize: 18,
        color: Colors.textSecondary,
        marginBottom: 16,
        textAlign: 'center',
    },
    statusContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
        backgroundColor: Colors.surface,
        paddingHorizontal: 16,
        paddingVertical: 8,
        borderRadius: 20,
        borderWidth: 1,
        borderColor: Colors.border,
    },
    statusDot: {
        width: 10,
        height: 10,
        borderRadius: 5,
    },
    statusText: {
        fontSize: 14,
        fontWeight: '600',
        color: Colors.textSecondary,
    },
    categoriesContainer: {
        flex: 1,
        gap: 16,
        justifyContent: 'center',
        maxWidth: 400,
        alignSelf: 'center',
        width: '100%',
    },
    categoryButton: {
        backgroundColor: Colors.surface,
        padding: 24,
        borderRadius: 24,
        alignItems: 'center',
        justifyContent: 'center',
        borderWidth: 2,
        borderColor: Colors.border,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.1,
        shadowRadius: 12,
        elevation: 5,
    },
    categoryButtonText: {
        fontSize: 24,
        fontWeight: 'bold',
        color: Colors.text,
    },
    categorySubtext: {
        fontSize: 14,
        color: Colors.textSecondary,
        marginTop: 4,
    },
    backButton: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 20,
        padding: 8,
        gap: 8,
    },
    backButtonText: {
        fontSize: 16,
        fontWeight: '600',
        color: Colors.primary,
    },
    selectedCategoryTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        color: Colors.text,
        marginBottom: 16,
        marginLeft: 4,
    },
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    sentenceGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 140, // Increased spacing significantly
        justifyContent: 'center',
        paddingHorizontal: 10,
    },
    sentenceButton: {
        width: 80,
        height: 80,
        borderRadius: 40, // Circle shape
        backgroundColor: '#58CC02', // Duolingo Green
        alignItems: 'center',
        justifyContent: 'center',

        borderColor: '#58CC02', // Hide other borders by matching bg, or just use transparent
        borderBottomColor: '#46A302', // Darker green for 3D effect
        // Remove shadow/elevation for cleaner 3D look
        elevation: 0,
        shadowOpacity: 0,
    },
    completedButton: {
        backgroundColor: '#FFC800', // Gold for completed
        borderColor: '#FFC800',
        borderBottomColor: '#D7A700', // Darker gold
    },
    sentenceButtonText: {
        fontSize: 26,
        fontWeight: 'bold',
        color: '#ffffff',
        textShadowColor: 'rgba(0, 0, 0, 0.2)',
        textShadowOffset: { width: 1, height: 1 },
        textShadowRadius: 2,
    },
    completedButtonText: {
        color: '#ffffff', // Keep white for contrast
    },
    checkIcon: {
        position: 'absolute',
        top: -5,
        right: -5,
        backgroundColor: Colors.success,
        borderRadius: 10,
        width: 20,
        height: 20,
        alignItems: 'center',
        justifyContent: 'center',
        borderWidth: 1.5,
        borderColor: 'transparent',
    },
    sentenceButtonTextCompleted: {
        color: Colors.success,
    },
    loadingText: {
        textAlign: 'center',
        fontSize: 16,
        color: Colors.textSecondary,
        padding: 20,
        width: '100%', // Ensure it takes full width in flex wrap
    },
    emptyText: {
        textAlign: 'center',
        fontSize: 16,
        color: Colors.textSecondary,
        padding: 20,
        width: '100%', // Ensure it takes full width in flex wrap
    },
    shine: {
        position: 'absolute',
        top: 8,
        left: 14,
        width: 30,
        height: 15,
        borderRadius: 10,
        backgroundColor: 'rgba(255, 255, 255, 0.4)',
        transform: [{ rotate: '-25deg' }],
    },
});;
