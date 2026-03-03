import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator, Image, ImageBackground } from 'react-native';
import { getStories } from '../services/api';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

// Image Mapping (In a real app, this might come from the backend or a separate config)
const storyImages = {
  'story_dutugemunu': require('../../assets/images/story_cover_dutugemunu.png'), 
  'story_prince_saliya': require('../../assets/images/story_cover_prince_saliya.png'),
  // Default fallback if ID doesn't match
  'default': require('../../assets/adaptive-icon.png') 
};

export default function DashboardScreen({ navigation }) {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStories();
  }, []);

  const loadStories = async () => {
    setLoading(true);
    const data = await getStories();
    setStories(data);
    setLoading(false);
  };

  const getStoryImage = (id) => {
      return storyImages[id] || storyImages['default'];
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity 
      activeOpacity={0.9}
      style={styles.cardContainer}
      onPress={() => navigation.navigate('Story', { storyId: item.id, title: item.title })}
    >
      <ImageBackground
        source={getStoryImage(item.id)}
        style={styles.bgImage}
        imageStyle={{ borderRadius: 16 }}
      >
        <LinearGradient
          colors={['transparent', 'rgba(0,0,0,0.8)']}
          style={styles.gradient}
        >
          <View style={styles.cardContent}>
            <View style={styles.textContainer}>
                <Text style={styles.categoryTag}>INTERACTIVE STORY</Text>
                <Text style={styles.title}>{item.title}</Text>
                <Text style={styles.subtitle}>Tap to start your adventure</Text>
            </View>
            <View style={styles.playButton}>
                <Ionicons name="play" size={24} color="white" style={{ marginLeft: 4 }} />
            </View>
          </View>
        </LinearGradient>
      </ImageBackground>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#FF8C00" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.headerTitle}>Story Library</Text>
      <FlatList
        data={stories}
        renderItem={renderItem}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
    paddingTop: 20,
    paddingHorizontal: 16,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '800',
    color: '#1A1A1A',
    marginBottom: 20,
    marginTop: 10,
    letterSpacing: 0.5,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  list: {
    paddingBottom: 40,
  },
  cardContainer: {
    height: 220,
    marginBottom: 20,
    borderRadius: 16,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    backgroundColor: 'white', 
  },
  bgImage: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  gradient: {
    flex: 1,
    borderRadius: 16,
    justifyContent: 'flex-end',
    padding: 20,
  },
  cardContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },
  textContainer: {
    flex: 1,
    marginRight: 10,
  },
  categoryTag: {
    color: '#FFD700',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 4,
    letterSpacing: 1,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
    textShadowColor: 'rgba(0, 0, 0, 0.75)',
    textShadowOffset: {width: 0, height: 1},
    textShadowRadius: 3,
  },
  subtitle: {
    fontSize: 14,
    color: '#E0E0E0',
    fontWeight: '500',
  },
  playButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#FF8C00',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 5,
  }
});
