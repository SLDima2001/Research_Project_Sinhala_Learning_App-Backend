/**
 * useSentences Hook
 * Fetches sentences from backend API with offline fallback
 * Implements network detection and caching
 */
import { useState, useCallback, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import Config from '../constants/Config';
import { OFFLINE_SENTENCES } from '../constants/offlineSentences';

export interface Sentence {
    id: string;
    text: string;
    words: string[];
    hasAudio?: boolean;
    audioPath?: string;
    translation?: string;
    difficulty?: string;
    completed?: boolean;
    timings?: { word: string; start: number; end: number }[];
}

export interface UseSentencesReturn {
    sentences: Sentence[];
    currentSentence: Sentence | null;
    isLoading: boolean;
    error: string | null;
    isOnline: boolean;
    refetch: (category: string, count?: number) => Promise<void>;
    nextSentence: () => void;
    previousSentence: () => void;
    selectSentence: (id: string) => void;
    currentIndex: number;
}

const CACHE_KEY = 'cached_sentences';

export const useSentences = (count: number = 20): UseSentencesReturn => {
    const [sentences, setSentences] = useState<Sentence[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [isConnected, setIsConnected] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Monitor network status
    useEffect(() => {
        const unsubscribe = NetInfo.addEventListener(state => {
            setIsConnected(state.isConnected ?? false);
        });
        return () => unsubscribe();
    }, []);

    // Cache helper
    const cacheSentences = async (data: Sentence[]) => {
        try {
            await AsyncStorage.setItem(CACHE_KEY, JSON.stringify(data));
        } catch (e) {
            console.warn('Failed to cache sentences', e);
        }
    };

    // Initialize from cache or offline on mount
    useEffect(() => {
        const loadInitialData = async () => {
            // Only load from cache if we haven't loaded anything yet
            if (sentences.length > 0) return;

            try {
                const cached = await AsyncStorage.getItem(CACHE_KEY);
                if (cached) {
                    const data = JSON.parse(cached);
                    console.log(`Loaded ${data.length} cached sentences`);
                    setSentences(data);
                    setIsLoading(false);
                    return;
                }
            } catch (e) { console.warn(e); }

            // Fallback
            console.log('No cache, loading offline sentences defaults');
            setSentences(OFFLINE_SENTENCES);
            setIsLoading(false);
        };
        loadInitialData();
    }, []);

    // Fetch sentences based on category
    const fetchSentences = useCallback(async (category: string = 'offline', fetchCount: number = 40): Promise<void> => {
        setIsLoading(true);
        setError(null);

        try {
            let newSentences: Sentence[] = [];

            // Handle Offline Category
            if (category === 'offline') {
                console.log('Loading offline sentences');
                await new Promise(resolve => setTimeout(resolve, 2500)); // Increased delay for animation
                newSentences = OFFLINE_SENTENCES;
            }
            // Check connection for other categories
            else if (!isConnected) {
                console.log('Offline mode detected, falling back to offline sentences');
                await new Promise(resolve => setTimeout(resolve, 2500)); // Consistent delay
                newSentences = OFFLINE_SENTENCES;
                setError('Offline mode: Showing offline sentences');
            }
            else {
                // Add artificial delay for online fetch as well to show the cute chicken
                await new Promise(resolve => setTimeout(resolve, 2500));

                const difficulty = category.toLowerCase();
                const url = `${Config.API_BASE_URL}/api/sentences/random/${difficulty}?count=${fetchCount}`;
                console.log('Fetching sentences from:', url);

                const response = await fetch(url, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' },
                });

                if (!response.ok) {
                    if (response.status === 404) {
                        newSentences = [];
                    } else {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                } else {
                    const data = await response.json();
                    const fetchedSentences = data.sentences || [];
                    newSentences = fetchedSentences.map((s: any) => ({
                        ...s,
                        difficulty: s.difficulty || difficulty
                    }));
                }
            }

            setSentences(newSentences);
            setCurrentIndex(0);
            cacheSentences(newSentences); // Cache for PracticeScreen

        } catch (err) {
            console.error('Error fetching sentences:', err);
            setError(err instanceof Error ? err.message : 'Failed to fetch sentences');
            setSentences(OFFLINE_SENTENCES);
        } finally {
            setIsLoading(false);
        }
    }, [isConnected]);

    // Navigation
    const nextSentence = useCallback(() => {
        setCurrentIndex(prev => (prev + 1) % sentences.length);
    }, [sentences.length]);

    const previousSentence = useCallback(() => {
        setCurrentIndex(prev => (prev - 1 + sentences.length) % sentences.length);
    }, [sentences.length]);

    const selectSentence = useCallback((id: string) => {
        const index = sentences.findIndex(s => s.id === id);
        if (index !== -1) setCurrentIndex(index);
    }, [sentences]);

    return {
        sentences,
        currentSentence: sentences[currentIndex] || null,
        isLoading,
        error,
        isOnline: isConnected,
        refetch: fetchSentences,
        nextSentence,
        previousSentence,
        selectSentence,
        currentIndex
    };
};
