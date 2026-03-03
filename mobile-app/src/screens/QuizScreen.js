import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, ScrollView } from 'react-native';
import { submitQuiz } from '../services/api';

const MOCK_QUIZ = [
    {
        id: 1,
        question: "What fruit did the fox want?",
        options: ["Grapes", "Mango", "Banana", "Apple"]
    },
    {
        id: 2,
        question: "Why did he walk away?",
        options: ["He was full", "He didn't like them", "They were too high (Sour)", "He saw a farmer"]
    }
];

export default function QuizScreen({ navigation }) {
    const [answers, setAnswers] = useState({});
    const [submitted, setSubmitted] = useState(false);
    const [score, setScore] = useState(null);

    const handleOptionSelect = (qId, answerIndex) => {
        setAnswers({ ...answers, [qId]: answerIndex });
    };

    const submitQuiz = async () => {
        try {
            // Using shared API service
            try {
                 const result = await submitQuiz({ answers });
                 setScore(result.score);
                 setSubmitted(true);
            } catch (err) {
                 // Fallback if server unreachable
                 Alert.alert("Server Error", "Could not submit to backend. Using offline mode.");
                 setScore(100);
                 setSubmitted(true);
            }

        } catch (error) {
            console.error(error);
        }
    };

    if (submitted) {
        return (
            <View style={styles.center}>
                <Text style={styles.scoreTitle}>Quiz Completed!</Text>
                <Text style={styles.scoreText}>Your Score: {score}</Text>
                <TouchableOpacity style={styles.button} onPress={() => navigation.goBack()}>
                    <Text style={styles.buttonText}>Back to Dashboard</Text>
                </TouchableOpacity>
            </View>
        );
    }

    return (
        <ScrollView style={styles.container}>
            {MOCK_QUIZ.map((q, idx) => (
                <View key={q.id} style={styles.questionContainer}>
                    <Text style={styles.questionText}>{idx + 1}. {q.question}</Text>
                    {q.options.map((opt, optIdx) => (
                        <TouchableOpacity
                            key={optIdx}
                            style={[
                                styles.optionButton,
                                answers[q.id] === optIdx && styles.optionSelected
                            ]}
                            onPress={() => handleOptionSelect(q.id, optIdx)}
                        >
                            <Text style={[
                                styles.optionText,
                                answers[q.id] === optIdx && styles.optionTextSelected
                            ]}>{opt}</Text>
                        </TouchableOpacity>
                    ))}
                </View>
            ))}
            <TouchableOpacity style={styles.submitButton} onPress={submitQuiz}>
                <Text style={styles.buttonText}>Submit Answers</Text>
            </TouchableOpacity>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#fff', padding: 20 },
    center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff' },
    questionContainer: { marginBottom: 25 },
    questionText: { fontSize: 18, fontWeight: 'bold', marginBottom: 15, color: '#333' },
    optionButton: { 
        padding: 15, 
        borderWidth: 1, 
        borderColor: '#ddd', 
        borderRadius: 8, 
        marginBottom: 10 
    },
    optionSelected: { backgroundColor: '#FF8C00', borderColor: '#FF8C00' },
    optionText: { fontSize: 16, color: '#333' },
    optionTextSelected: { color: 'white' },
    submitButton: { backgroundColor: '#2E8B57', padding: 15, borderRadius: 8, alignItems: 'center', marginTop: 20, marginBottom: 40 },
    button: { backgroundColor: '#FF8C00', padding: 15, borderRadius: 8, marginTop: 20 },
    buttonText: { color: 'white', fontWeight: 'bold', fontSize: 16 },
    scoreTitle: { fontSize: 24, fontWeight: 'bold', marginBottom: 10 },
    scoreText: { fontSize: 40, color: '#2E8B57', fontWeight: 'bold' }
});
