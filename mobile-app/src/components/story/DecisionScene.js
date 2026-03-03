import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';

const IMAGE_PLACEHOLDER = 'https://via.placeholder.com/300x200.png?text=Decision+Point';

export default function DecisionScene({ data, onNext }) {
    return (
        <View style={styles.container}>
            <Text style={styles.question}>{data.text}</Text>
            
            <Image 
                source={{ uri: IMAGE_PLACEHOLDER }} 
                style={styles.image} 
                resizeMode="cover"
            />

            <View style={styles.choices}>
                {data.choices.map((choice, idx) => (
                    <TouchableOpacity 
                        key={idx} 
                        style={styles.button}
                        onPress={() => onNext(choice.next_scene_id)}
                    >
                        <Text style={styles.buttonText}>{choice.text}</Text>
                    </TouchableOpacity>
                ))}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, padding: 20, alignItems: 'center', justifyContent: 'center' },
    question: { fontSize: 22, fontWeight: 'bold', textAlign: 'center', marginBottom: 20 },
    image: { width: '100%', height: 200, borderRadius: 10, marginBottom: 30 },
    choices: { width: '100%', gap: 15 },
    button: { backgroundColor: '#6200EE', padding: 15, borderRadius: 8, alignItems: 'center' },
    buttonText: { color: 'white', fontSize: 16, fontWeight: 'bold' }
});
