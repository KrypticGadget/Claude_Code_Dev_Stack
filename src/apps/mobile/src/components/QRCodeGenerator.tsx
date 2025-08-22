/**
 * QR Code Generator Component for React Native
 * Generates and displays QR codes for mobile sharing
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Share,
  Alert,
  Dimensions,
  ScrollView,
  Platform
} from 'react-native';
import QRCode from 'react-native-qrcode-svg';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Icon from 'react-native-vector-icons/MaterialIcons';

interface QRCodeData {
  type: string;
  sessionId: string;
  token?: string;
  url?: string;
  serviceName?: string;
  description?: string;
  expiresAt?: number;
  deepLink?: string;
}

interface QRCodeGeneratorProps {
  data: QRCodeData;
  size?: number;
  onGenerated?: (qrData: QRCodeData) => void;
  onError?: (error: string) => void;
}

const { width } = Dimensions.get('window');
const defaultSize = Math.min(width - 80, 300);

const QRCodeGeneratorComponent: React.FC<QRCodeGeneratorProps> = ({
  data,
  size = defaultSize,
  onGenerated,
  onError
}) => {
  const [qrRef, setQrRef] = useState<any>(null);
  const [isSharing, setIsSharing] = useState(false);

  // Generate QR code data string
  const qrDataString = JSON.stringify(data);

  // Handle QR code generation
  const handleQRGenerated = useCallback(() => {
    onGenerated?.(data);
  }, [data, onGenerated]);

  // Share QR code
  const shareQRCode = async () => {
    if (!qrRef) {
      Alert.alert('Error', 'QR code not ready for sharing');
      return;
    }

    setIsSharing(true);

    try {
      // Get QR code as base64
      qrRef.toDataURL((dataURL: string) => {
        const shareOptions = {
          title: data.serviceName || 'Claude Code Access',
          message: `${data.description || 'Connect to Claude Code'}\n\n${data.url || data.deepLink || ''}`,
          url: `data:image/png;base64,${dataURL}`,
        };

        Share.share(shareOptions)
          .then(() => {
            console.log('QR code shared successfully');
          })
          .catch((error) => {
            console.error('Error sharing QR code:', error);
            onError?.('Failed to share QR code');
          })
          .finally(() => {
            setIsSharing(false);
          });
      });
    } catch (error) {
      console.error('Error generating QR code for sharing:', error);
      onError?.('Failed to generate QR code for sharing');
      setIsSharing(false);
    }
  };

  // Save QR code data
  const saveQRCode = async () => {
    try {
      const savedQRCodes = await AsyncStorage.getItem('savedQRCodes');
      const qrCodes = savedQRCodes ? JSON.parse(savedQRCodes) : [];
      
      const newQRCode = {
        ...data,
        savedAt: Date.now(),
        id: `qr_${Date.now()}`
      };

      qrCodes.push(newQRCode);
      await AsyncStorage.setItem('savedQRCodes', JSON.stringify(qrCodes));
      
      Alert.alert('Success', 'QR code saved successfully');
    } catch (error) {
      console.error('Error saving QR code:', error);
      Alert.alert('Error', 'Failed to save QR code');
    }
  };

  // Copy data to clipboard
  const copyToClipboard = () => {
    const textToCopy = data.url || data.deepLink || qrDataString;
    
    // React Native doesn't have built-in clipboard, would need @react-native-clipboard/clipboard
    // For now, show the data in an alert
    Alert.alert(
      'QR Code Data',
      textToCopy,
      [
        { text: 'Close', style: 'cancel' },
        { text: 'Share', onPress: () => Share.share({ message: textToCopy }) }
      ]
    );
  };

  // Format expiration time
  const formatExpirationTime = (timestamp: number) => {
    const now = Date.now();
    const diff = timestamp - now;
    
    if (diff <= 0) return 'Expired';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `Expires in ${hours}h ${minutes}m`;
    } else {
      return `Expires in ${minutes}m`;
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>{data.serviceName || 'Claude Code Access'}</Text>
        {data.description && (
          <Text style={styles.description}>{data.description}</Text>
        )}
      </View>

      {/* QR Code */}
      <View style={styles.qrContainer}>
        <View style={styles.qrWrapper}>
          <QRCode
            value={qrDataString}
            size={size}
            backgroundColor="white"
            color="black"
            logo={require('../assets/logo.png')} // You would need to add this
            logoSize={size * 0.15}
            logoBackgroundColor="white"
            logoMargin={2}
            logoBorderRadius={10}
            getRef={(ref) => setQrRef(ref)}
            onError={(error) => {
              console.error('QR Code generation error:', error);
              onError?.('Failed to generate QR code');
            }}
          />
        </View>
      </View>

      {/* Information */}
      <View style={styles.infoContainer}>
        <View style={styles.infoRow}>
          <Icon name="info" size={20} color="#666" />
          <Text style={styles.infoText}>
            Type: {data.type.replace('_', ' ').toUpperCase()}
          </Text>
        </View>
        
        {data.expiresAt && (
          <View style={styles.infoRow}>
            <Icon name="schedule" size={20} color="#666" />
            <Text style={[
              styles.infoText,
              data.expiresAt <= Date.now() ? styles.expiredText : styles.activeText
            ]}>
              {formatExpirationTime(data.expiresAt)}
            </Text>
          </View>
        )}

        {data.sessionId && (
          <View style={styles.infoRow}>
            <Icon name="vpn-key" size={20} color="#666" />
            <Text style={styles.infoText}>
              Session: {data.sessionId.slice(0, 8)}...
            </Text>
          </View>
        )}
      </View>

      {/* Action Buttons */}
      <View style={styles.actionContainer}>
        <TouchableOpacity
          style={[styles.actionButton, styles.primaryButton]}
          onPress={shareQRCode}
          disabled={isSharing}
        >
          <Icon name="share" size={24} color="white" />
          <Text style={styles.primaryButtonText}>
            {isSharing ? 'Sharing...' : 'Share QR Code'}
          </Text>
        </TouchableOpacity>

        <View style={styles.secondaryActions}>
          <TouchableOpacity
            style={[styles.actionButton, styles.secondaryButton]}
            onPress={saveQRCode}
          >
            <Icon name="save" size={20} color="#007AFF" />
            <Text style={styles.secondaryButtonText}>Save</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.secondaryButton]}
            onPress={copyToClipboard}
          >
            <Icon name="content-copy" size={20} color="#007AFF" />
            <Text style={styles.secondaryButtonText}>Copy</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Usage Instructions */}
      <View style={styles.instructionsContainer}>
        <Text style={styles.instructionsTitle}>How to use:</Text>
        <Text style={styles.instructionsText}>
          1. Share this QR code with others
        </Text>
        <Text style={styles.instructionsText}>
          2. Scan with any QR code scanner
        </Text>
        <Text style={styles.instructionsText}>
          3. Follow the connection instructions
        </Text>
        {data.expiresAt && (
          <Text style={styles.instructionsText}>
            4. Note: This QR code will expire automatically
          </Text>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  contentContainer: {
    padding: 20,
    alignItems: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: 30,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 8,
  },
  description: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  qrContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  qrWrapper: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 5,
  },
  infoContainer: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
    width: '100%',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  infoText: {
    fontSize: 16,
    color: '#333',
    marginLeft: 10,
    flex: 1,
  },
  expiredText: {
    color: '#FF6B6B',
    fontWeight: 'bold',
  },
  activeText: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  actionContainer: {
    width: '100%',
    marginBottom: 30,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 25,
    paddingVertical: 15,
    paddingHorizontal: 20,
    marginBottom: 10,
  },
  primaryButton: {
    backgroundColor: '#007AFF',
  },
  secondaryButton: {
    backgroundColor: 'white',
    borderWidth: 2,
    borderColor: '#007AFF',
    flex: 1,
    marginHorizontal: 5,
  },
  primaryButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 10,
  },
  secondaryButtonText: {
    color: '#007AFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  secondaryActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  instructionsContainer: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    width: '100%',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  instructionsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  instructionsText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
});

export default QRCodeGeneratorComponent;