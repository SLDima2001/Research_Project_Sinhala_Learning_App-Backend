import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

export default function InteractionOverlay({ interaction, onOptionSelect }) {
    if (!interaction) return null;

    return (
        <View style={styles.overlay}>
            <View style={styles.card}>
                <Text style={styles.title}>{interaction.type === 'decision' ? 'Make a Choice' : 'Quick Quiz'}</Text>
                <Text style={styles.question}>{interaction.text}</Text>
                
                <View style={styles.options}>
                    {interaction.options.map((option, idx) => (
                        <TouchableOpacity 
                            key={idx} 
                            style={styles.button}
                            onPress={() => onOptionSelect(option)}
                        >
                            <Text style={styles.buttonText}>{option.text}</Text>
                        </TouchableOpacity>
                    ))}
                </View>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    overlay: {
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.7)', // Semi-transparent black
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 10
    },
    card: {
        width: '80%',
        backgroundColor: 'white',
        borderRadius: 15,
        padding: 20,
        alignItems: 'center',
        elevation: 10
    },
    title: {
        fontSize: 16,
        textTransform: 'uppercase',
        color: '#666',
        marginBottom: 10
    },
    question: {
        fontSize: 22,
        fontWeight: 'bold',
        textAlign: 'center',
        marginBottom: 20,
        color: '#333'
    },
    options: {
        width: '100%',
        gap: 15
    },
    button: {
        backgroundColor: '#FF8C00',
        padding: 15,
        borderRadius: 8,
        alignItems: 'center',
        width: '100%'
    },
    buttonText: {
        color: 'white',
        fontSize: 18,
        fontWeight: 'bold'
    }
});
