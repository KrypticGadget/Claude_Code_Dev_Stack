/**
 * Claude Code Dev Stack v3.0 - React Native Mobile App
 * Ported from Flutter (@9cat) - MIT License
 * 
 * Features:
 * - SSH connection to Claude Code instances
 * - Real-time chat interface
 * - Voice recognition support
 * - WebSocket integration with backend
 */

import React, { useEffect, useState } from 'react';
import {
  StyleSheet,
  StatusBar,
  SafeAreaView,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import io from 'socket.io-client';

// Screens
import ConnectionScreen from './src/screens/ConnectionScreen';
import ChatScreen from './src/screens/ChatScreen';

// Context
import { AppStateProvider } from './src/context/AppStateContext';

const Stack = createStackNavigator();

const App: React.FC = () => {
  const [socket, setSocket] = useState<any>(null);

  useEffect(() => {
    // Connect to WebSocket backend
    const socketConnection = io('http://localhost:8080', {
      transports: ['websocket'],
    });

    socketConnection.on('connect', () => {
      console.log('Connected to backend WebSocket');
      // Report mobile app status
      socketConnection.emit('mobile-status', {
        status: 'connected',
        platform: 'react-native',
        version: '3.0.0'
      });
    });

    socketConnection.on('disconnect', () => {
      console.log('Disconnected from backend WebSocket');
    });

    setSocket(socketConnection);

    return () => {
      socketConnection.disconnect();
    };
  }, []);

  return (
    <AppStateProvider socket={socket}>
      <SafeAreaView style={styles.container}>
        <StatusBar
          barStyle="light-content"
          backgroundColor="#1E1E1E"
        />
        <NavigationContainer>
          <Stack.Navigator
            initialRouteName="Connection"
            screenOptions={{
              headerStyle: {
                backgroundColor: '#1E1E1E',
              },
              headerTintColor: '#FFFFFF',
              headerTitleStyle: {
                fontWeight: 'bold',
              },
            }}
          >
            <Stack.Screen
              name="Connection"
              component={ConnectionScreen}
              options={{
                title: 'Claude Code Mobile',
                headerShown: true,
              }}
            />
            <Stack.Screen
              name="Chat"
              component={ChatScreen}
              options={{
                title: 'Claude Code Chat',
                headerShown: true,
              }}
            />
          </Stack.Navigator>
        </NavigationContainer>
      </SafeAreaView>
    </AppStateProvider>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1E1E1E',
  },
});

export default App;