import React, { useEffect, useState, useRef } from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet, ScrollView, Animated } from 'react-native';
import { Audio, Video, ResizeMode } from 'expo-av';

const IMAGE_PLACEHOLDER = 'https://via.placeholder.com/300x200.png?text=Story+Image';

export default function NarrativeScene({ data, onNext, onWordClick }) {
    const [sound, setSound] = useState(null);
    const fadeAnim = useRef(new Animated.Value(0)).current; 
    const videoRef = useRef(null);

    useEffect(() => {
        // Reset animation
        fadeAnim.setValue(0);
        
        // Start Text Animation (Line by line effect simulated by fade in)
        Animated.timing(fadeAnim, {
            toValue: 1,
            duration: 2000, 
            useNativeDriver: true,
        }).start();

        // Auto-play Audio (Mock logic: Try to load if local, or just simulate)
        playAudio();

        return () => {
            if (sound) sound.unloadAsync();
        };
    }, [data]);

    const playAudio = async () => {
        // In a real app, we would load `data.audio`. 
        // Since we don't have files, we just log it.
        // console.log("Playing audio:", data.audio);
    };

    const renderText = () => {
        const words = data.text.split(' ');
        const vocab = data.vocabulary || [];

        return (
            <Animated.View style={{ opacity: fadeAnim }}>
                <Text style={styles.text}>
                    {words.map((word, index) => {
                        const cleanWord = word.replace(/[.,!?"'()]/g, '');
                        const vocabItem = vocab.find(v => v.word === cleanWord || v.word === word);
                        
                        if (vocabItem) {
                            return (
                                <Text key={index} style={styles.highlight} onPress={() => onWordClick(vocabItem)}>
                                    {word}{' '}
                                </Text>
                            );
                        }
                        return <Text key={index}>{word} </Text>;
                    })}
                </Text>
            </Animated.View>
        );
    };

    return (
        <ScrollView contentContainerStyle={styles.container}>
            {/* Video or Image Support */}
            {data.video ? (
                 <Video
                    ref={videoRef}
                    style={styles.video}
                    source={{ uri: 'https://d23dyxeqlo5psv.cloudfront.net/big_buck_bunny.mp4' }} // Placeholder video
                    useNativeControls
                    resizeMode={ResizeMode.CONTAIN}
                    isLooping
                    shouldPlay
                 />
            ) : (
                <Image 
                    source={{ uri: IMAGE_PLACEHOLDER }} 
                    style={styles.image} 
                    resizeMode="cover"
                />
            )}
            
            <View style={styles.textContainer}>
                {renderText()}
            </View>

            <View style={styles.choices}>
                {data.choices && data.choices.map((choice, idx) => (
                    <TouchableOpacity 
                        key={idx} 
                        style={styles.button}
                        onPress={() => onNext(choice.next_scene_id)}
                    >
                        <Text style={styles.buttonText}>{choice.text}</Text>
                    </TouchableOpacity>
                ))}
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { padding: 20, paddingBottom: 50 },
    image: { width: '100%', height: 200, borderRadius: 10, marginBottom: 20 },
    video: { width: '100%', height: 200, borderRadius: 10, marginBottom: 20 },
    textContainer: { marginBottom: 30 },
    text: { fontSize: 18, lineHeight: 28, color: '#333' },
    highlight: { color: '#FF8C00', fontWeight: 'bold', textDecorationLine: 'underline' },
    choices: { gap: 10 },
    button: { backgroundColor: '#FF8C00', padding: 15, borderRadius: 8, alignItems: 'center' },
    buttonText: { color: 'white', fontSize: 16, fontWeight: 'bold' }
});
