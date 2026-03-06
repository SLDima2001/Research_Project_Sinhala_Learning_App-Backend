import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import Colors from '../constants/Colors';

export default function RootLayout() {
    return (
        <>
            <StatusBar style="auto" />
            <Stack
                screenOptions={{
                    headerStyle: {
                        backgroundColor: '#747250',
                    },
                    headerTintColor: Colors.textLight,
                    headerTitleAlign: 'center',
                    headerTitleStyle: {
                        fontWeight: 'bold',
                        fontSize: 20,
                    },
                    animation: 'slide_from_right',
                }}
            >
                <Stack.Screen
                    name="index"
                    options={{
                        title: 'සිංහල පන්තිය',
                        headerShown: true,
                    }}
                />
                <Stack.Screen
                    name="practice"
                    options={{
                        title: 'Practice',
                        headerShown: true,
                    }}
                />
                <Stack.Screen
                    name="results"
                    options={{
                        title: 'Results',
                        headerShown: true,
                    }}
                />
            </Stack>
        </>
    );
}
