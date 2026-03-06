import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import Config from '../constants/Config';

export interface WebSocketMessage {
    type: string;
    [key: string]: any;
}

export const useWebSocket = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const socketRef = useRef<Socket | null>(null);
    const messageHandlersRef = useRef<Map<string, (data: any) => void>>(new Map());

    // Connect to WebSocket
    const connect = useCallback(() => {
        try {
            const socket = io(Config.WEBSOCKET_URL, {
                transports: ['websocket'],
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionAttempts: 5,
            });

            socket.on('connect', () => {
                console.log('WebSocket connected');
                setIsConnected(true);
                setError(null);
            });

            socket.on('disconnect', () => {
                console.log('WebSocket disconnected');
                setIsConnected(false);
            });

            socket.on('error', (err: any) => {
                console.error('WebSocket error:', err);
                setError(err.message || 'WebSocket error');
            });

            // Handle incoming messages
            socket.onAny((eventName: string, data: any) => {
                const handler = messageHandlersRef.current.get(eventName);
                if (handler) {
                    handler(data);
                }
            });

            socketRef.current = socket;
        } catch (err: any) {
            setError(err.message || 'Failed to connect');
        }
    }, []);

    // Disconnect from WebSocket
    const disconnect = useCallback(() => {
        if (socketRef.current) {
            socketRef.current.disconnect();
            socketRef.current = null;
            setIsConnected(false);
        }
    }, []);

    // Send message
    const sendMessage = useCallback((type: string, data: any = {}) => {
        if (socketRef.current && isConnected) {
            socketRef.current.emit(type, data);
        } else {
            console.warn('Cannot send message: WebSocket not connected');
        }
    }, [isConnected]);

    // Register message handler
    const onMessage = useCallback((type: string, handler: (data: any) => void) => {
        messageHandlersRef.current.set(type, handler);
    }, []);

    // Unregister message handler
    const offMessage = useCallback((type: string) => {
        messageHandlersRef.current.delete(type);
    }, []);

    // Auto-connect on mount
    useEffect(() => {
        connect();
        return () => {
            disconnect();
        };
    }, [connect, disconnect]);

    return {
        isConnected,
        error,
        connect,
        disconnect,
        sendMessage,
        onMessage,
        offMessage,
    };
};

export default useWebSocket;
