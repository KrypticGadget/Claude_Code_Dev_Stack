/**
 * Chat Screen - Main chat interface with Claude Code
 * Ported from Flutter ChatScreen (@9cat) - MIT License
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  Alert,
  Platform,
  KeyboardAvoidingView,
  Dimensions,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useNavigation } from '@react-navigation/native';
import { useAppState } from '../context/AppStateContext';
import { ChatMessage, MessageType } from '../models/ChatMessage';

interface MessageBubbleProps {
  message: ChatMessage;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const getMessageStyle = () => {
    switch (message.type) {
      case MessageType.USER:
        return {
          prefix: '➤ ',
          textColor: '#60A5FA', // Blue
          backgroundColor: '#1E3A8A20',
        };
      case MessageType.ASSISTANT:
        return {
          prefix: '',
          textColor: '#4ADE80', // Green
          backgroundColor: '#15803D20',
        };
      case MessageType.SYSTEM:
        return {
          prefix: '[SYSTEM] ',
          textColor: '#FBBF24', // Yellow
          backgroundColor: '#92400E20',
        };
      case MessageType.ERROR:
        return {
          prefix: '[ERROR] ',
          textColor: '#F87171', // Red
          backgroundColor: '#DC262620',
        };
      default:
        return {
          prefix: '',
          textColor: '#9CA3AF',
          backgroundColor: '#37415120',
        };
    }
  };

  const formatTime = (timestamp: Date): string => {
    return `${timestamp.getHours().toString().padStart(2, '0')}:${timestamp
      .getMinutes()
      .toString()
      .padStart(2, '0')}`;
  };

  const style = getMessageStyle();

  return (
    <View style={[styles.messageBubble, { backgroundColor: style.backgroundColor }]}>
      <Text style={styles.timestamp}>{formatTime(message.timestamp)}</Text>
      <View style={styles.messageContent}>
        <Text style={[styles.messageText, { color: style.textColor }]}>
          <Text style={styles.messagePrefix}>{style.prefix}</Text>
          {message.content}
        </Text>
      </View>
    </View>
  );
};

const ChatScreen: React.FC = () => {
  const navigation = useNavigation();
  const { state, sendCommand, disconnect, clearMessages, updateCurrentInput, startVoiceInput, stopVoiceInput } = useAppState();
  const [inputText, setInputText] = useState('');
  const flatListRef = useRef<FlatList>(null);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (state.messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [state.messages]);

  useEffect(() => {
    // Sync input text with state
    setInputText(state.currentInput);
  }, [state.currentInput]);

  const handleSendMessage = async () => {
    const message = inputText.trim();
    if (!message) return;

    try {
      await sendCommand(message);
      setInputText('');
    } catch (error) {
      Alert.alert('Error', 'Failed to send message');
    }
  };

  const handleVoiceToggle = async () => {
    if (state.isListening) {
      await stopVoiceInput();
    } else {
      await startVoiceInput();
    }
  };

  const handleDisconnect = () => {
    Alert.alert(
      'Disconnect',
      'Are you sure you want to disconnect from the server?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Disconnect',
          style: 'destructive',
          onPress: () => {
            disconnect();
            navigation.navigate('Connection' as never);
          },
        },
      ]
    );
  };

  const renderMessage = ({ item }: { item: ChatMessage }) => (
    <MessageBubble message={item} />
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Icon name="terminal" size={20} color="#4ADE80" />
          <Text style={styles.headerTitle}>Claude-Code CLI</Text>
        </View>
        <View style={styles.headerRight}>
          <TouchableOpacity onPress={handleDisconnect} style={styles.headerButton}>
            <Icon
              name={state.isConnected ? 'cloud-done' : 'cloud-off'}
              size={24}
              color={state.isConnected ? '#4ADE80' : '#F87171'}
            />
          </TouchableOpacity>
          <TouchableOpacity onPress={clearMessages} style={styles.headerButton}>
            <Icon name="clear-all" size={24} color="#9CA3AF" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Messages */}
      <FlatList
        ref={flatListRef}
        data={state.messages}
        keyExtractor={(item) => item.id}
        renderItem={renderMessage}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContent}
        showsVerticalScrollIndicator={false}
      />

      {/* Input Area */}
      <View style={styles.inputArea}>
        <View style={styles.inputContainer}>
          <Text style={[styles.inputPrefix, { color: state.isConnected ? '#60A5FA' : '#F87171' }]}>
            {state.isConnected ? '➤ ' : '✗ '}
          </Text>
          <TextInput
            style={styles.textInput}
            value={inputText}
            onChangeText={(text) => {
              setInputText(text);
              updateCurrentInput(text);
            }}
            placeholder={state.isConnected ? 'Enter your command...' : 'Not connected to server'}
            placeholderTextColor="#6B7280"
            multiline
            maxLength={1000}
            editable={state.isConnected}
            onSubmitEditing={handleSendMessage}
            blurOnSubmit={false}
          />
        </View>
        
        <View style={styles.inputButtons}>
          {state.isVoiceEnabled && (
            <TouchableOpacity
              style={[
                styles.voiceButton,
                state.isListening ? styles.voiceButtonActive : null,
                !state.isConnected ? styles.buttonDisabled : null,
              ]}
              onPress={handleVoiceToggle}
              disabled={!state.isConnected}
            >
              <Icon
                name={state.isListening ? 'mic' : 'mic-none'}
                size={20}
                color={state.isListening ? '#FFFFFF' : '#9CA3AF'}
              />
            </TouchableOpacity>
          )}
          
          <TouchableOpacity
            style={[
              styles.sendButton,
              (!state.isConnected || !inputText.trim()) ? styles.buttonDisabled : null,
            ]}
            onPress={handleSendMessage}
            disabled={!state.isConnected || !inputText.trim()}
          >
            <Icon name="send" size={20} color="#FFFFFF" />
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D1117',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#161B22',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#21262D',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginLeft: 8,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  headerRight: {
    flexDirection: 'row',
  },
  headerButton: {
    marginLeft: 12,
    padding: 4,
  },
  messagesList: {
    flex: 1,
  },
  messagesContent: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  messageBubble: {
    marginVertical: 2,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    marginHorizontal: 4,
  },
  timestamp: {
    fontSize: 11,
    color: '#6B7280',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    marginBottom: 2,
  },
  messageContent: {
    flexDirection: 'row',
    flex: 1,
  },
  messageText: {
    fontSize: 14,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    lineHeight: 20,
    flex: 1,
  },
  messagePrefix: {
    fontWeight: 'bold',
  },
  inputArea: {
    backgroundColor: '#2D2D30',
    borderTopWidth: 1,
    borderTopColor: '#3E3E42',
    paddingHorizontal: 16,
    paddingVertical: 12,
    paddingBottom: Platform.OS === 'ios' ? 24 : 12,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#0D1117',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#30363D',
    paddingHorizontal: 12,
    paddingVertical: 12,
    marginBottom: 8,
    minHeight: 44,
  },
  inputPrefix: {
    fontSize: 14,
    fontWeight: 'bold',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    marginRight: 8,
    marginTop: Platform.OS === 'android' ? 2 : 0,
  },
  textInput: {
    flex: 1,
    fontSize: 14,
    color: '#FFFFFF',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    maxHeight: 120,
    includeFontPadding: false,
    textAlignVertical: 'top',
    ...Platform.select({
      android: {
        paddingVertical: 0,
      },
    }),
  },
  inputButtons: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  voiceButton: {
    backgroundColor: '#374151',
    borderRadius: 20,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  voiceButtonActive: {
    backgroundColor: '#DC2626',
  },
  sendButton: {
    backgroundColor: '#3B82F6',
    borderRadius: 20,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
});

export default ChatScreen;