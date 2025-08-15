/**
 * Connection Screen - Server connection setup
 * Ported from Flutter ConnectionScreen (@9cat) - MIT License
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  ActivityIndicator,
  Platform,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useNavigation } from '@react-navigation/native';
import { useAppState } from '../context/AppStateContext';
import { ConnectionConfigImpl } from '../models/ConnectionConfig';

const ConnectionScreen: React.FC = () => {
  const navigation = useNavigation();
  const { state, connectToServer } = useAppState();
  
  const [serverUrl, setServerUrl] = useState('http://192.168.2.178:64008');
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('password123');
  const [obscurePassword, setObscurePassword] = useState(true);
  const [errors, setErrors] = useState<{[key: string]: string}>({});

  const validateForm = (): boolean => {
    const newErrors: {[key: string]: string} = {};

    if (!serverUrl.trim()) {
      newErrors.serverUrl = 'Please enter server URL';
    } else if (!serverUrl.startsWith('http://') && !serverUrl.startsWith('https://')) {
      newErrors.serverUrl = 'URL must start with http:// or https://';
    }

    if (!username.trim()) {
      newErrors.username = 'Please enter username';
    }

    if (!password.trim()) {
      newErrors.password = 'Please enter password';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleConnect = async () => {
    if (!validateForm()) return;

    const connection = new ConnectionConfigImpl({
      serverUrl: serverUrl.trim(),
      username: username.trim(),
      password: password.trim(),
    });

    const success = await connectToServer(connection);

    if (success) {
      navigation.navigate('Chat' as never);
    }
  };

  const renderTextField = (
    value: string,
    onChangeText: (text: string) => void,
    label: string,
    iconName: string,
    secureTextEntry: boolean = false,
    error?: string
  ) => (
    <View style={styles.inputContainer}>
      <Text style={styles.inputLabel}>{label}</Text>
      <View style={[styles.inputWrapper, error ? styles.inputError : null]}>
        <Icon name={iconName} size={20} color="#9CA3AF" style={styles.inputIcon} />
        <TextInput
          style={styles.textInput}
          value={value}
          onChangeText={onChangeText}
          secureTextEntry={secureTextEntry}
          placeholderTextColor="#6B7280"
          autoCapitalize="none"
          autoCorrect={false}
        />
        {label === 'Password' && (
          <TouchableOpacity
            onPress={() => setObscurePassword(!obscurePassword)}
            style={styles.eyeIcon}
          >
            <Icon
              name={obscurePassword ? 'visibility' : 'visibility-off'}
              size={20}
              color="#9CA3AF"
            />
          </TouchableOpacity>
        )}
      </View>
      {error && <Text style={styles.errorText}>{error}</Text>}
    </View>
  );

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      <View style={styles.header}>
        <Icon name="cloud" size={80} color="#3B82F6" />
        <Text style={styles.title}>Connect to Claude-Code Server</Text>
        <Text style={styles.subtitle}>
          Enter your proxy server details to start coding with Claude-Code
        </Text>
      </View>

      <View style={styles.form}>
        {renderTextField(
          serverUrl,
          setServerUrl,
          'Server URL',
          'language',
          false,
          errors.serverUrl
        )}

        {renderTextField(
          username,
          setUsername,
          'Username',
          'person',
          false,
          errors.username
        )}

        {renderTextField(
          password,
          setPassword,
          'Password',
          'lock',
          obscurePassword,
          errors.password
        )}

        <TouchableOpacity
          style={[
            styles.connectButton,
            state.isConnecting ? styles.connectButtonDisabled : null
          ]}
          onPress={handleConnect}
          disabled={state.isConnecting}
        >
          {state.isConnecting ? (
            <ActivityIndicator color="#FFFFFF" size="small" />
          ) : (
            <Text style={styles.connectButtonText}>Connect</Text>
          )}
        </TouchableOpacity>

        <Text style={styles.credentialsHint}>
          Default credentials: admin/password123, developer/dev2024, user/user123
        </Text>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Claude-Code Mobile v3.0{'\n'}
          Original Flutter app by @9cat (MIT License)
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1E1E1E',
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: 24,
    paddingVertical: 40,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
    marginTop: 16,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#9CA3AF',
    textAlign: 'center',
    lineHeight: 22,
  },
  form: {
    marginBottom: 40,
  },
  inputContainer: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#F3F4F6',
    marginBottom: 8,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#2D2D30',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'transparent',
    paddingHorizontal: 12,
    height: 48,
  },
  inputError: {
    borderColor: '#EF4444',
  },
  inputIcon: {
    marginRight: 12,
  },
  textInput: {
    flex: 1,
    fontSize: 16,
    color: '#FFFFFF',
    includeFontPadding: false,
    textAlignVertical: 'center',
    ...Platform.select({
      android: {
        paddingVertical: 0,
      },
    }),
  },
  eyeIcon: {
    padding: 4,
  },
  errorText: {
    fontSize: 12,
    color: '#EF4444',
    marginTop: 4,
  },
  connectButton: {
    backgroundColor: '#3B82F6',
    borderRadius: 8,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 16,
  },
  connectButtonDisabled: {
    opacity: 0.6,
  },
  connectButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  credentialsHint: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 16,
    lineHeight: 16,
  },
  footer: {
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 16,
  },
});

export default ConnectionScreen;