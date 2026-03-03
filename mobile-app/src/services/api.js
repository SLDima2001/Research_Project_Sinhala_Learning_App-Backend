import axios from 'axios';
import { Platform } from 'react-native';

// Android Emulator uses 10.0.2.2 for localhost
const API_URL = Platform.OS === 'android' ? 'http://10.0.2.2:8000/api' : 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 5000,
});

export const getStories = async () => {
    try {
        const response = await api.get('/stories');
        return response.data;
    } catch (error) {
        console.error("Error fetching stories:", error);
        return [];
    }
};

export const getStory = async (id) => {
    try {
        const response = await api.get(`/stories/${id}`);
        return response.data;
    } catch (error) {
        console.error("Error fetching story:", error);
        return null;
    }
};

export const submitQuiz = async (data) => {
    try {
        const response = await api.post('/quiz/submit', data);
        return response.data;
    } catch (error) {
        console.error("Error submitting quiz:", error);
        throw error;
    }
};
