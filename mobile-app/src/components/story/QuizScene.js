import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

export default function QuizScene({ data, onNext, onScore }) {
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [score, setScore] = useState(0);
    const [showResults, setShowResults] = useState(false);

    const handleAnswer = (option) => {
        const currentQuestion = data.questions[currentQuestionIndex];
        let newScore = score;
        
        if (option === currentQuestion.correct_answer) {
            newScore += 1;
            setScore(newScore);
        }

        if (currentQuestionIndex < data.questions.length - 1) {
            setCurrentQuestionIndex(currentQuestionIndex + 1);
        } else {
            finishQuiz(newScore);
        }
    };

    const finishQuiz = (finalScore) => {
        const points = finalScore * 20; // 20 points per question
        onScore(points);
        onNext(data.next_scene_id, { quizScore: finalScore, totalQuestions: data.questions.length });
    };

    const currentQuestion = data.questions[currentQuestionIndex];

    return (
        <View style={styles.container}>
            <Text style={styles.header}>Quiz Time!</Text>
            <Text style={styles.progress}>Question {currentQuestionIndex + 1}/{data.questions.length}</Text>
            
            <View style={styles.card}>
                <Text style={styles.question}>{currentQuestion.question}</Text>
                
                {currentQuestion.options.map((option, idx) => (
                    <TouchableOpacity 
                        key={idx} 
                        style={styles.optionButton}
                        onPress={() => handleAnswer(option)}
                    >
                        <Text style={styles.optionText}>{option}</Text>
                    </TouchableOpacity>
                ))}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, padding: 20, justifyContent: 'center' },
    header: { fontSize: 24, fontWeight: 'bold', textAlign: 'center', marginBottom: 10, color: '#FF8C00' },
    progress: { textAlign: 'center', marginBottom: 20, color: '#666' },
    card: { backgroundColor: 'white', padding: 20, borderRadius: 15, elevation: 5 },
    question: { fontSize: 18, marginBottom: 20, fontWeight: 'bold' },
    optionButton: { backgroundColor: '#f0f0f0', padding: 15, borderRadius: 10, marginBottom: 10 },
    optionText: { fontSize: 16 }
});
