/**
 * QR Code Scanner Component for Claude Code Mobile Access
 * React Native component for scanning QR codes and handling deep links
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Alert,
  Linking,
  Platform,
  Dimensions,
  TouchableOpacity,
  SafeAreaView,
  StatusBar
} from 'react-native';
import QRCodeScanner from 'react-native-qrcode-scanner';
import { RNCamera } from 'react-native-camera';
import { request, PERMISSIONS, RESULTS } from 'react-native-permissions';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Icon from 'react-native-vector-icons/MaterialIcons';

interface QRCodeData {
  type: string;
  sessionId: string;
  token: string;
  tunnelUrl?: string;
  appUrl?: string;
  deepLink?: string;
  serviceName?: string;
  description?: string;
  expiresAt: number;
}

interface QRCodeScannerProps {
  onScanSuccess?: (data: QRCodeData) => void;
  onScanError?: (error: string) => void;
  onConnectionEstablished?: (connectionInfo: any) => void;
  autoConnect?: boolean;
}

const { width, height } = Dimensions.get('window');

const QRCodeScannerComponent: React.FC<QRCodeScannerProps> = ({
  onScanSuccess,
  onScanError,
  onConnectionEstablished,
  autoConnect = true
}) => {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [isScanning, setIsScanning] = useState(true);
  const [flashOn, setFlashOn] = useState(false);
  const [scannedData, setScannedData] = useState<QRCodeData | null>(null);
  const [connecting, setConnecting] = useState(false);

  // Request camera permission
  useEffect(() => {
    requestCameraPermission();
  }, []);

  const requestCameraPermission = async () => {
    try {
      const permission = Platform.select({
        ios: PERMISSIONS.IOS.CAMERA,
        android: PERMISSIONS.ANDROID.CAMERA,
      });

      if (!permission) {
        setHasPermission(false);
        return;
      }

      const result = await request(permission);
      
      switch (result) {
        case RESULTS.GRANTED:
          setHasPermission(true);
          break;
        case RESULTS.DENIED:
        case RESULTS.BLOCKED:
          setHasPermission(false);
          Alert.alert(
            'Camera Permission Required',
            'Please enable camera access in settings to scan QR codes.',
            [
              { text: 'Cancel', style: 'cancel' },
              { text: 'Open Settings', onPress: () => Linking.openSettings() }
            ]
          );
          break;
        default:
          setHasPermission(false);
      }
    } catch (error) {
      console.error('Permission request error:', error);
      setHasPermission(false);
    }
  };

  // Handle QR code scan
  const onSuccess = useCallback(async (e: any) => {
    if (!isScanning) return;

    setIsScanning(false);

    try {
      // Parse QR code data
      let qrData: QRCodeData;
      
      try {
        qrData = JSON.parse(e.data);
      } catch (parseError) {
        // Handle simple URL format
        if (e.data.startsWith('http')) {
          qrData = {
            type: 'simple_url',
            sessionId: Date.now().toString(),
            token: '',
            tunnelUrl: e.data,
            serviceName: 'Claude Code',
            description: 'Direct URL access',
            expiresAt: Date.now() + 24 * 60 * 60 * 1000 // 24 hours
          };
        } else {
          throw new Error('Invalid QR code format');
        }
      }

      // Validate expiration
      if (qrData.expiresAt && Date.now() > qrData.expiresAt) {
        Alert.alert('Expired QR Code', 'This QR code has expired. Please scan a new one.');
        setIsScanning(true);
        return;
      }

      setScannedData(qrData);
      onScanSuccess?.(qrData);

      // Store scanned data
      await AsyncStorage.setItem('lastQRScan', JSON.stringify({
        ...qrData,
        scannedAt: Date.now()
      }));

      if (autoConnect) {
        await handleConnection(qrData);
      } else {
        // Show connection confirmation
        Alert.alert(
          qrData.serviceName || 'Connect to Service',
          qrData.description || 'Would you like to connect?',
          [
            { text: 'Cancel', onPress: () => setIsScanning(true) },
            { text: 'Connect', onPress: () => handleConnection(qrData) }
          ]
        );
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Invalid QR code';
      onScanError?.(errorMessage);
      Alert.alert('Scan Error', errorMessage);
      setIsScanning(true);
    }
  }, [isScanning, onScanSuccess, onScanError, autoConnect]);

  // Handle connection to service
  const handleConnection = async (qrData: QRCodeData) => {
    setConnecting(true);

    try {
      // Validate token if present
      if (qrData.token) {
        const validationResponse = await fetch('/api/qr/validate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: qrData.token })
        });

        if (!validationResponse.ok) {
          throw new Error('Invalid or expired token');
        }

        const validation = await validationResponse.json();
        if (!validation.valid) {
          throw new Error(validation.error || 'Token validation failed');
        }
      }

      // Determine connection method based on type
      switch (qrData.type) {
        case 'tunnel_access':
        case 'simple_url':
          await handleTunnelConnection(qrData);
          break;
        case 'mobile_access':
          await handleMobileAppConnection(qrData);
          break;
        case 'session_access':
          await handleSessionConnection(qrData);
          break;
        case 'time_limited_access':
          await handleTimeLimitedConnection(qrData);
          break;
        case 'multi_service_access':
          await handleMultiServiceConnection(qrData);
          break;
        default:
          throw new Error(`Unsupported connection type: ${qrData.type}`);
      }

      onConnectionEstablished?.(qrData);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Connection failed';
      Alert.alert('Connection Error', errorMessage);
      onScanError?.(errorMessage);
    } finally {
      setConnecting(false);
      setIsScanning(true);
    }
  };

  // Handle tunnel connection
  const handleTunnelConnection = async (qrData: QRCodeData) => {
    if (qrData.tunnelUrl) {
      // Store connection info
      await AsyncStorage.setItem('activeConnection', JSON.stringify({
        type: 'tunnel',
        url: qrData.tunnelUrl,
        serviceName: qrData.serviceName,
        connectedAt: Date.now(),
        sessionId: qrData.sessionId
      }));

      // Open in WebView or external browser
      const supported = await Linking.canOpenURL(qrData.tunnelUrl);
      if (supported) {
        await Linking.openURL(qrData.tunnelUrl);
      } else {
        throw new Error('Cannot open tunnel URL');
      }
    }
  };

  // Handle mobile app connection
  const handleMobileAppConnection = async (qrData: QRCodeData) => {
    if (qrData.deepLink) {
      const supported = await Linking.canOpenURL(qrData.deepLink);
      if (supported) {
        await Linking.openURL(qrData.deepLink);
      } else if (qrData.appUrl) {
        await Linking.openURL(qrData.appUrl);
      }
    }
  };

  // Handle session connection
  const handleSessionConnection = async (qrData: QRCodeData) => {
    // Store session data and navigate to chat
    await AsyncStorage.setItem('sessionData', JSON.stringify({
      sessionId: qrData.sessionId,
      token: qrData.token,
      connectedAt: Date.now()
    }));

    // Navigate to chat screen or trigger connection
    // This would typically use navigation
  };

  // Handle time-limited connection
  const handleTimeLimitedConnection = async (qrData: QRCodeData) => {
    // Similar to tunnel connection but with time awareness
    await handleTunnelConnection(qrData);
    
    // Set up expiration reminder
    const timeRemaining = qrData.expiresAt - Date.now();
    if (timeRemaining > 0 && timeRemaining < 10 * 60 * 1000) { // Less than 10 minutes
      Alert.alert(
        'Time Limited Access',
        `This connection will expire in ${Math.round(timeRemaining / 60000)} minutes.`
      );
    }
  };

  // Handle multi-service connection
  const handleMultiServiceConnection = async (qrData: QRCodeData) => {
    // Show service selection dialog
    // For now, just connect to the first available service
    await handleTunnelConnection(qrData);
  };

  // Toggle flashlight
  const toggleFlash = () => {
    setFlashOn(!flashOn);
  };

  // Restart scanning
  const restartScanning = () => {
    setIsScanning(true);
    setScannedData(null);
  };

  if (hasPermission === null) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.loadingText}>Requesting camera permission...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.centerContainer}>
        <Icon name="camera-alt" size={64} color="#ccc" style={styles.icon} />
        <Text style={styles.errorText}>Camera access denied</Text>
        <Text style={styles.errorSubtext}>
          Please enable camera permission in settings to scan QR codes.
        </Text>
        <TouchableOpacity
          style={styles.button}
          onPress={() => Linking.openSettings()}
        >
          <Text style={styles.buttonText}>Open Settings</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000" />
      
      {isScanning && !connecting ? (
        <QRCodeScanner
          onRead={onSuccess}
          reactivate={isScanning}
          reactivateTimeout={2000}
          flashMode={flashOn ? RNCamera.Constants.FlashMode.torch : RNCamera.Constants.FlashMode.off}
          cameraStyle={styles.camera}
          containerStyle={styles.scannerContainer}
          showMarker={true}
          markerStyle={styles.marker}
          topContent={
            <View style={styles.topContent}>
              <Text style={styles.centerText}>
                Scan QR code to connect to Claude Code
              </Text>
            </View>
          }
          bottomContent={
            <View style={styles.bottomContent}>
              <TouchableOpacity
                style={[styles.actionButton, flashOn && styles.activeButton]}
                onPress={toggleFlash}
              >
                <Icon 
                  name={flashOn ? "flash-on" : "flash-off"} 
                  size={24} 
                  color={flashOn ? "#000" : "#fff"} 
                />
              </TouchableOpacity>
            </View>
          }
        />
      ) : (
        <View style={styles.centerContainer}>
          {connecting ? (
            <>
              <Icon name="wifi" size={64} color="#007AFF" style={styles.icon} />
              <Text style={styles.loadingText}>Connecting...</Text>
              {scannedData && (
                <Text style={styles.serviceText}>
                  {scannedData.serviceName || 'Claude Code'}
                </Text>
              )}
            </>
          ) : (
            <>
              <Icon name="check-circle" size={64} color="#4CAF50" style={styles.icon} />
              <Text style={styles.successText}>QR Code Scanned!</Text>
              {scannedData && (
                <View style={styles.infoContainer}>
                  <Text style={styles.serviceText}>{scannedData.serviceName}</Text>
                  <Text style={styles.descriptionText}>{scannedData.description}</Text>
                </View>
              )}
              <TouchableOpacity
                style={styles.button}
                onPress={restartScanning}
              >
                <Text style={styles.buttonText}>Scan Another</Text>
              </TouchableOpacity>
            </>
          )}
        </View>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000',
    padding: 20,
  },
  scannerContainer: {
    flex: 1,
  },
  camera: {
    height: height,
    width: width,
  },
  marker: {
    borderColor: '#007AFF',
    borderRadius: 10,
  },
  topContent: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'flex-end',
    alignItems: 'center',
    paddingBottom: 20,
  },
  bottomContent: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'flex-start',
    alignItems: 'center',
    paddingTop: 20,
  },
  centerText: {
    fontSize: 18,
    color: '#fff',
    textAlign: 'center',
    fontWeight: '500',
  },
  actionButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 30,
    padding: 15,
    marginHorizontal: 10,
  },
  activeButton: {
    backgroundColor: '#fff',
  },
  icon: {
    marginBottom: 20,
  },
  loadingText: {
    fontSize: 18,
    color: '#fff',
    textAlign: 'center',
    marginBottom: 10,
  },
  successText: {
    fontSize: 24,
    color: '#4CAF50',
    textAlign: 'center',
    fontWeight: 'bold',
    marginBottom: 20,
  },
  errorText: {
    fontSize: 20,
    color: '#FF6B6B',
    textAlign: 'center',
    fontWeight: 'bold',
    marginBottom: 10,
  },
  errorSubtext: {
    fontSize: 16,
    color: '#ccc',
    textAlign: 'center',
    marginBottom: 30,
    paddingHorizontal: 20,
  },
  infoContainer: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 10,
    padding: 20,
    marginBottom: 30,
    alignItems: 'center',
  },
  serviceText: {
    fontSize: 20,
    color: '#fff',
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 5,
  },
  descriptionText: {
    fontSize: 16,
    color: '#ccc',
    textAlign: 'center',
  },
  button: {
    backgroundColor: '#007AFF',
    borderRadius: 25,
    paddingHorizontal: 30,
    paddingVertical: 15,
    marginTop: 20,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default QRCodeScannerComponent;