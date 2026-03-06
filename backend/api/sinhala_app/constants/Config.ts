import Constants from 'expo-constants';
import { Platform } from 'react-native';
import * as Device from 'expo-device';

// Helper to determine the correct backend URL
const getBackendUrl = () => {
    const PORT = 5002;

    // Android Emulator special loopback IP
    if (Platform.OS === 'android' && !Device.isDevice) {
        return `http://10.0.2.2:${PORT}`;
    }

    // iOS Simulator uses standard localhost
    if (Platform.OS === 'ios' && !Device.isDevice) {
        return `http://localhost:${PORT}`;
    }

    // For physical devices, rely on Expo's host URI (LAN IP)
    if (Constants.expoConfig?.hostUri) {
        const ip = Constants.expoConfig.hostUri.split(':')[0];
        return `http://${ip}:${PORT}`;
    }

    // Fallback to the hardcoded LAN IP if automatic detection fails
    return 'http://10.98.174.160:5002';
};

const BASE_URL = getBackendUrl();

// WebSocket and API Configuration
export const Config = {
    // WebSocket server URL
    WEBSOCKET_URL: BASE_URL, 
    // API endpoints
    API_BASE_URL: BASE_URL,

    // Audio settings
    AUDIO: {
        SAMPLE_RATE: 16000,
        CHANNELS: 1,
        ENCODING: 'pcm_16bit',
        CHUNK_SIZE: 4096,
    },

    // Recording settings
    RECORDING: {
        MAX_DURATION: 30000, // 30 seconds max
        MIN_DURATION: 500, // 0.5 seconds min
    },

    // Offline mode settings
    OFFLINE: {
        ENABLED: true,
        CACHE_AUDIO: true,
        CACHE_SENTENCES: true,
        MAX_CACHE_SIZE: 100 * 1024 * 1024, // 100MB
    },

    // Audio fallback settings
    AUDIO_FALLBACK: {
        USE_TEXT_TO_SPEECH: true, // Use expo-speech when audio files unavailable
        TTS_LANGUAGE: 'si-LK', // Sinhala language code
    },

    // Network settings
    NETWORK: {
        CONNECT_TIMEOUT: 5000, // 5 seconds
        REQUEST_TIMEOUT: 10000, // 10 seconds
        RETRY_ATTEMPTS: 2,
    },

    // App settings
    APP: {
        POINTS_PER_CORRECT_WORD: 10,
        POINTS_PER_SENTENCE: 50,
        HIGHLIGHT_DURATION: 300, // ms per word during playback
    },
};

export default Config;
