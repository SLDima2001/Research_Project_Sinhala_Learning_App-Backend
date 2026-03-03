import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert, Dimensions, useWindowDimensions, ToastAndroid, Platform, Modal, Image } from 'react-native';
import { Video, ResizeMode } from 'expo-av';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Asset } from 'expo-asset';
import * as ScreenOrientation from 'expo-screen-orientation';
import { getStory } from '../services/api';
// Legacy Components
import NarrativeScene from '../components/story/NarrativeScene';
import DecisionScene from '../components/story/DecisionScene';
import ActivityScene from '../components/story/ActivityScene';
import QuizScene from '../components/story/QuizScene';
// New Video Components
import InteractionOverlay from '../components/story/InteractionOverlay';

export default function StoryScreen({ route, navigation }) {
    const { storyId } = route.params;
    const { width, height } = useWindowDimensions();
    const isLandscape = width > height;

    const [story, setStory] = useState(null);
    const [loading, setLoading] = useState(true);

    // Legacy State
    const [currentSceneId, setCurrentSceneId] = useState('scene_1_intro');
    
    // Video Engine State
    const videoRef = useRef(null);
    const [currentSegmentId, setCurrentSegmentId] = useState('segment_1_intro');
    const [interactionData, setInteractionData] = useState(null);
    const [playbackStatus, setPlaybackStatus] = useState(null);
    const [videoSource, setVideoSource] = useState(null); // Local URI state
    const [userHistory, setUserHistory] = useState([]); 
    
    // UI State
    const [showScoreModal, setShowScoreModal] = useState(false);
    const [finalScore, setFinalScore] = useState(0); 

    useEffect(() => {
        loadStoryData();
        return () => {
             ScreenOrientation.lockAsync(ScreenOrientation.OrientationLock.PORTRAIT_UP);
        };
    }, []);

    const loadStoryData = async () => {
        const data = await getStory(storyId);
        if (data) {
            console.log("RECEIVED STORY DATA:", JSON.stringify(data, null, 2)); 
            setStory(data);
            if (data.type === 'video_interactive') {
               try {
                   await ScreenOrientation.lockAsync(ScreenOrientation.OrientationLock.DEFAULT);
               } catch (error) { console.warn(error); }
               setCurrentSegmentId(Object.keys(data.segments)[0]); 
            } else if (data.scenes && !data.scenes['scene_1_intro']) {
               setCurrentSceneId(Object.keys(data.scenes)[0]);
            }
        }
        setLoading(false);
    };

    // ==========================================
    // VIDEO ASSET LOADER (Fixes NAL Error)
    // ==========================================
    useEffect(() => {
        if (!story || story.type !== 'video_interactive') return;

        const segment = story.segments[currentSegmentId];
        const videoId = segment?.video_id;

        const loadVideo = async () => {
            if (!segment) return;

            // Priority 1: Direct URL from Database (User Request: "videos path only add the database")
            if (segment.video_url && segment.video_url.trim() !== '') {
                console.log(`Using Database Video URL: ${segment.video_url}`);
                setVideoSource({ uri: segment.video_url });
                return;
            }

            // Priority 2: Legacy Local Asset Map ("show the previous wize")
            if (!videoId) return;
            
            try {
                // Return if we already have this source loaded (optimisation)
                // But simple approach is safer: reset -> load -> set
                setVideoSource(null); 

                const { getVideoSource } = require('../services/videoMap');
                const resourceId = getVideoSource(videoId);
                
                if (resourceId) {
                    console.log(`Downloading asset for: ${videoId}`);
                    const asset = Asset.fromModule(resourceId);
                    await asset.downloadAsync();
                    
                    const uri = asset.localUri || asset.uri;
                    console.log(`Asset ready: ${uri}`);
                    setVideoSource({ uri: uri });
                } else {
                     console.warn(`No local asset found for video_id: ${videoId}`);
                }

            } catch (error) {
                console.error("Asset Download Error:", error);
                ToastAndroid.show("Video Load Error", ToastAndroid.SHORT);
            }
        };

        loadVideo();

    }, [currentSegmentId, story]); // Re-run when segment changes


    // ==========================================
    // VIDEO LOGIC
    // ==========================================
    const handleVideoUpdate = (status) => {
        if (!status.isLoaded || !story || story.type !== 'video_interactive') return;
        setPlaybackStatus(status);

        const segment = story.segments[currentSegmentId];
        if (!segment) return; 
        
        // Match end time to finish segment
        if ((status.isPlaying && status.positionMillis >= segment.end_time) || status.didJustFinish) {
            videoRef.current.pauseAsync();
            const nextId = segment.next_segment_id;
            
            if (story.interactions[nextId]) {
                setInteractionData(story.interactions[nextId]);
            } else if (nextId === 'end_screen') {
                handleVideoEnd();
            } else {
                 changeSegment(nextId);
            }
        }
    };


    const handleOptionSelect = (option) => {
        setUserHistory(prev => [...prev, {
            interaction: interactionData.text,
            choice: option.text,
            isCorrect: option.is_correct
        }]);

        if (interactionData.type === 'quiz' && Platform.OS === 'android') {
            ToastAndroid.show(
                option.is_correct ? "Correct! Great job!" : "Incorrect, but let's continue!",
                ToastAndroid.SHORT
            );
        }
        proceedToNext(option.next_segment_id);
    };

    const proceedToNext = async (nextId) => {
        // 1. Check if next step is another interaction (Chained Quiz)
        if (story.interactions[nextId]) {
            setInteractionData(story.interactions[nextId]);
            return;
        }

        // 2. Hide current overlay if moving to video/end
        setInteractionData(null);
        
        if (nextId === 'end_screen') {
            handleVideoEnd();
            return;
        }

        // 3. Change Video Segment
        changeSegment(nextId);
    };

    const changeSegment = async (segmentId) => {
        const segment = story.segments[segmentId];
        if (!segment) return;
        
        // Clean switch
        setInteractionData(null);
        setPlaybackStatus(null);
        
        setStory(prev => ({...prev, _reloading: true}));
        
        // Small delay to allow UI to clear before mounting new video
        setTimeout(() => {
            setCurrentSegmentId(segmentId);
            setStory(prev => ({...prev, _reloading: false}));
        }, 100);
    };

    const handleVideoEnd = async () => {
        const score = userHistory.filter(h => h.isCorrect).length;
        const resultData = {
            storyId,
            mode: 'video_interactive',
            points: score * 10,
            history: userHistory,
            completedAt: new Date().toISOString()
        };

        try {
            const existing = await AsyncStorage.getItem('user_progress');
            let progress = existing ? JSON.parse(existing) : [];
            progress.push(resultData);
            await AsyncStorage.setItem('user_progress', JSON.stringify(progress));
        } catch (e) {
            console.error("Failed to save progress", e);
        }

        setFinalScore(score);
        setShowScoreModal(true);
    };

    // ==========================================
    // RENDER
    // ==========================================
    if (loading || !story) return <View style={styles.center}><Text>Loading...</Text></View>;

    // 1. VIDEO INTERACTIVE MODE
    if (story.type === 'video_interactive') {
        const segment = story.segments[currentSegmentId];
        const videoId = segment?.video_id;

        // Transition State
        if (story._reloading || !videoSource) {
            return (
                <View style={[styles.center, {backgroundColor: 'black'}]}>
                    <Text style={{color: 'white'}}>Loading Video...</Text>
                </View>
            );
        }

        return (
            <View style={styles.container}>
                <View style={styles.videoWrapper}>
                    <Video
                        key={`${videoId}_${currentSegmentId}`}
                        ref={videoRef}
                        style={styles.fullscreenVideo}
                        source={videoSource}
                        useNativeControls={true} 
                        resizeMode={isLandscape ? ResizeMode.COVER : ResizeMode.CONTAIN}
                        shouldPlay={true}
                        progressUpdateIntervalMillis={100}
                        onPlaybackStatusUpdate={handleVideoUpdate}
                        onLoad={() => {
                            if (segment && segment.start_time > 0) {
                                videoRef.current.setPositionAsync(segment.start_time);
                            }
                        }}
                        onError={(error) => {
                            console.error("VIDEO ERROR:", error);
                            ToastAndroid.show("Video Error: " + error, ToastAndroid.LONG);
                        }}
                    />
                </View>

                {/* DEBUG INFO */}
                {/* <View style={styles.debugBox}>
                    <Text style={styles.debugText}>DEBUG: {currentSegmentId}</Text>
                    <Text style={styles.debugText}>Vid: {videoId}</Text>
                    <Text style={styles.debugText}>Src: {videoSource?.uri ? 'Loaded' : 'Pending'}</Text>
                </View> */}

                {interactionData && (
                    <InteractionOverlay 
                        interaction={interactionData} 
                        onOptionSelect={handleOptionSelect} 
                    />
                )}

                {/* 3. FINAL SCORE MODAL */}
                <Modal
                    transparent={true}
                    visible={showScoreModal}
                    animationType="fade"
                    onRequestClose={() => navigation.goBack()}
                >
                    <View style={styles.modalOverlay}>
                        <View style={styles.modalCard}>
                            <Text style={styles.modalTitle}>Congratulations!</Text>
                            <Text style={styles.modalSubtitle}>You finished the story!</Text>
                            
                            <View style={styles.scoreContainer}>
                                <Text style={styles.scoreLabel}>Final Score</Text>
                                <Text style={styles.scoreValue}>{finalScore}</Text>
                            </View>

                            <TouchableOpacity 
                                style={styles.finishButton}
                                onPress={() => {
                                    setShowScoreModal(false);
                                    navigation.goBack();
                                }}
                            >
                                <Text style={styles.finishButtonText}>Finish Story</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </Modal>
            </View>
        );
    } 

    // 2. LEGACY SCENE MODE
    const scene = story.scenes[currentSceneId];
    if (!scene) return <View style={styles.center}><Text>Scene not found</Text></View>;
    const sceneType = scene.type || 'narrative';

    const handleLegacyNext = (nextId) => {
        if (!nextId) { Alert.alert("End", "Finished!", [{ text: "Back", onPress: () => navigation.goBack()}]); return;}
        setCurrentSceneId(nextId);
    };

    return (
        <View style={styles.container}>
            {sceneType === 'narrative' && <NarrativeScene data={scene} onNext={handleLegacyNext} />}
            {sceneType === 'decision' && <DecisionScene data={scene} onNext={handleLegacyNext} />}
            {sceneType === 'activity' && <ActivityScene data={scene} onNext={handleLegacyNext} />}
            {sceneType === 'quiz' && <QuizScene data={scene} onNext={handleLegacyNext} />}
            {/* 3. FINAL SCORE MODAL */}
            <Modal
                transparent={true}
                visible={showScoreModal}
                animationType="fade"
                onRequestClose={() => navigation.goBack()}
            >
                <View style={styles.modalOverlay}>
                    <View style={styles.modalCard}>
                        <Text style={styles.modalTitle}>Congratulations!</Text>
                        <Text style={styles.modalSubtitle}>You finished the story!</Text>
                        
                        <View style={styles.scoreContainer}>
                            <Text style={styles.scoreLabel}>Final Score</Text>
                            <Text style={styles.scoreValue}>{finalScore}</Text>
                        </View>

                        <TouchableOpacity 
                            style={styles.finishButton}
                            onPress={() => {
                                setShowScoreModal(false);
                                navigation.goBack();
                            }}
                        >
                            <Text style={styles.finishButtonText}>Finish Story</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </Modal>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#000', justifyContent: 'center' },
    center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    videoWrapper: { width: '100%', height: '100%', justifyContent: 'center', alignItems: 'center' },
    fullscreenVideo: { width: '100%', height: '100%' },
    debugBox: {
        position: 'absolute', top: 40, left: 20, 
        backgroundColor: 'rgba(0,0,0,0.5)', padding: 5, borderRadius: 5
    },
    debugText: { color: 'white', fontSize: 10 },
    // Modal Styles
    modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.8)', justifyContent: 'center', alignItems: 'center' },
    modalCard: { width: '80%', backgroundColor: 'white', borderRadius: 20, padding: 30, alignItems: 'center', elevation: 5 },
    modalTitle: { fontSize: 24, fontWeight: 'bold', marginBottom: 10, color: '#333' },
    modalSubtitle: { fontSize: 16, color: '#666', marginBottom: 20 },
    scoreContainer: { marginBottom: 30, alignItems: 'center' },
    scoreLabel: { fontSize: 14, textTransform: 'uppercase', color: '#888', letterSpacing: 1 },
    scoreValue: { fontSize: 48, fontWeight: 'bold', color: '#FFA500' },
    finishButton: { backgroundColor: '#FFA500', paddingVertical: 12, paddingHorizontal: 40, borderRadius: 25 },
    finishButtonText: { color: 'white', fontSize: 18, fontWeight: 'bold' }
});
