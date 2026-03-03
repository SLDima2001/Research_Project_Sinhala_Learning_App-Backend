import 'react-native-gesture-handler';
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import DashboardScreen from './src/screens/DashboardScreen';
import StoryScreen from './src/screens/StoryScreen';
import QuizScreen from './src/screens/QuizScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Dashboard">
        <Stack.Screen name="Dashboard" component={DashboardScreen} options={{ title: 'Story Library' }} />
        <Stack.Screen name="Story" component={StoryScreen} options={{ title: 'Read Story' }} />
        <Stack.Screen name="Quiz" component={QuizScreen} options={{ title: 'Quiz Time' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
