import React, { useState, useEffect } from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet, Alert } from 'react-native';

export default function ActivityScene({ data, onNext, onScore }) {
    const [selectedOption, setSelectedOption] = useState(null);
    const [isCorrect, setIsCorrect] = useState(null);

    useEffect(() => {
        console.log("ActivityScene loaded with data:", data);
    }, [data]);

    const handleOptionSelect = (option) => {
        setSelectedOption(option);
        const correct = option.is_correct;
        setIsCorrect(correct);

        if (correct) {
            onScore(10); // Award points
            Alert.alert("Correct!", "Well done!", [
                { text: "Continue", onPress: () => onNext(data.next_scene_id) }
            ]);
        } else {
            Alert.alert("Try Again", "That's not quite right.");
        }
    };

    if (!data) return <Text>Loading Activity...</Text>;

    return (
        <View style={styles.container}>
            <Text style={styles.debugInfo}>Type: {data.activity_type} | Opts: {data.options?.length}</Text>
            <Text style={styles.instruction}>{data.text || "Follow the instructions below:"}</Text>
            
            <View style={styles.optionsContainer}>
                {data.options.map((option, idx) => (
                    <TouchableOpacity 
                        key={idx} 
                        style={[
                            styles.optionCard,
                            // selectedOption?.id === option.id && (isCorrect ? styles.correct : styles.incorrect)
                        ]}
                        onPress={() => handleOptionSelect(option)}
                    >
                        {data.activity_type === 'matching' && (
                            <View style={styles.imagePlaceholder}>
                                <Text style={styles.placeholderText}>Image {idx + 1}</Text>
                            </View>
                        )}
                        
                        {(data.activity_type === 'selection' || option.text) && (
                             <Text style={styles.optionText}>{option.text || "Option"}</Text>
                        )}
                    </TouchableOpacity>
                ))}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, padding: 20, justifyContent: 'center', backgroundColor: '#fff' },
    debugInfo: { position: 'absolute', top: 40, right: 20, color: 'red', fontSize: 12 },
    instruction: { fontSize: 22, fontWeight: 'bold', marginBottom: 30, textAlign: 'center', color: '#333' },
    optionsContainer: { width: '100%', alignItems: 'center' }, // Simplified: Column layout
    optionCard: { 
        width: '90%', // Full width cards
        padding: 20, 
        backgroundColor: '#f9f9f9', 
        borderRadius: 10, 
        elevation: 3, 
        alignItems: 'center',
        borderWidth: 2,
        borderColor: '#ddd',
        marginBottom: 15 // Margin instead of gap
    },
    imagePlaceholder: { width: 80, height: 80, marginBottom: 10, backgroundColor: '#ccc', justifyContent: 'center', alignItems: 'center' },
    placeholderText: { fontSize: 12, color: '#666' },
    optionText: { fontSize: 16, fontWeight: 'bold', textAlign: 'center' },
    correct: { borderColor: '#4CAF50', backgroundColor: '#E8F5E9' },
    incorrect: { borderColor: '#F44336', backgroundColor: '#FFEBEE' }
});
