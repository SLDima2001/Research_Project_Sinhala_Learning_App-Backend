import Constants from 'expo-constants';
import { Platform } from 'react-native';
import * as Device from 'expo-device';


const getBackendUrl = () => {
    const PORT = 5002;

    if (Platform.OS === 'android' && !Device.isDevice) {
        return `http://10.0.2.2:${PORT}`;
    }

    if (Platform.OS === 'ios' && !Device.isDevice) {
        return `http://localhost:${PORT}`;
    }

    if (Constants.expoConfig?.hostUri) {
        const ip = Constants.expoConfig.hostUri.split(':')[0];
        return `http://${ip}:${PORT}`;
    }

    return 'http://10.98.174.160:5002';
};

const BASE_URL = getBackendUrl();


export const Config = {
    WEBSOCKET_URL: BASE_URL, 
    API_BASE_URL: BASE_URL,

    AUDIO: {
        SAMPLE_RATE: 16000,
        CHANNELS: 1,
        ENCODING: 'pcm_16bit',
        CHUNK_SIZE: 4096,
    },

    RECORDING: {
        MAX_DURATION: 30000, 
        MIN_DURATION: 500, 
    },

    OFFLINE: {
        ENABLED: true,
        CACHE_AUDIO: true,
        CACHE_SENTENCES: true,
        MAX_CACHE_SIZE: 100 * 1024 * 1024, 
    },

    AUDIO_FALLBACK: {
        USE_TEXT_TO_SPEECH: true, 
        TTS_LANGUAGE: 'si-LK', 
    },

    NETWORK: {
        CONNECT_TIMEOUT: 5000, 
        REQUEST_TIMEOUT: 10000, 
        RETRY_ATTEMPTS: 2,
    },

    APP: {
        POINTS_PER_CORRECT_WORD: 10,
        POINTS_PER_SENTENCE: 50,
        HIGHLIGHT_DURATION: 300, 
    },
};

export default Config;
