/**
 * QR Code Connection Service for Mobile
 * Handles QR code scanning, validation, and connection establishment
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { Linking, Alert } from 'react-native';

interface QRCodeData {
  type: string;
  sessionId: string;
  token?: string;
  tunnelUrl?: string;
  appUrl?: string;
  deepLink?: string;
  serviceName?: string;
  description?: string;
  expiresAt?: number;
  connectionInfo?: any;
}

interface ConnectionOptions {
  autoConnect?: boolean;
  timeout?: number;
  retryAttempts?: number;
}

interface ConnectionResult {
  success: boolean;
  connectionId?: string;
  error?: string;
  data?: any;
}

class QRConnectionService {
  private baseUrl: string;
  private connections: Map<string, any> = new Map();
  private connectionListeners: Set<Function> = new Set();

  constructor(baseUrl: string = 'http://localhost:8080') {
    this.baseUrl = baseUrl;
    this.loadStoredConnections();
  }

  /**
   * Load stored connections from AsyncStorage
   */
  private async loadStoredConnections() {
    try {
      const stored = await AsyncStorage.getItem('qr_connections');
      if (stored) {
        const connections = JSON.parse(stored);
        connections.forEach((conn: any) => {
          this.connections.set(conn.id, conn);
        });
      }
    } catch (error) {
      console.error('Failed to load stored connections:', error);
    }
  }

  /**
   * Save connections to AsyncStorage
   */
  private async saveConnections() {
    try {
      const connections = Array.from(this.connections.values());
      await AsyncStorage.setItem('qr_connections', JSON.stringify(connections));
    } catch (error) {
      console.error('Failed to save connections:', error);
    }
  }

  /**
   * Validate QR code data
   */
  async validateQRCode(qrData: QRCodeData): Promise<{ valid: boolean; error?: string }> {
    try {
      // Check expiration
      if (qrData.expiresAt && Date.now() > qrData.expiresAt) {
        return { valid: false, error: 'QR code has expired' };
      }

      // Validate token if present
      if (qrData.token) {
        const response = await fetch(`${this.baseUrl}/api/qr/validate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: qrData.token }),
        });

        if (!response.ok) {
          return { valid: false, error: 'Token validation failed' };
        }

        const result = await response.json();
        return result;
      }

      // Basic validation for non-token QR codes
      if (!qrData.type || !qrData.sessionId) {
        return { valid: false, error: 'Invalid QR code format' };
      }

      return { valid: true };
    } catch (error) {
      return { valid: false, error: 'Validation request failed' };
    }
  }

  /**
   * Process scanned QR code and establish connection
   */
  async processQRCode(
    qrData: QRCodeData,
    options: ConnectionOptions = {}
  ): Promise<ConnectionResult> {
    const { autoConnect = true, timeout = 30000, retryAttempts = 3 } = options;

    try {
      // Validate QR code
      const validation = await this.validateQRCode(qrData);
      if (!validation.valid) {
        return { success: false, error: validation.error };
      }

      // Store connection attempt
      const connectionId = `conn_${Date.now()}_${qrData.sessionId}`;
      const connection = {
        id: connectionId,
        qrData,
        status: 'connecting',
        createdAt: Date.now(),
        attempts: 0,
      };

      this.connections.set(connectionId, connection);
      await this.saveConnections();

      // Establish connection based on type
      let result: ConnectionResult;
      switch (qrData.type) {
        case 'tunnel_access':
        case 'simple_url':
          result = await this.connectToTunnel(qrData, connectionId, options);
          break;
        case 'mobile_access':
          result = await this.connectToMobileApp(qrData, connectionId, options);
          break;
        case 'session_access':
          result = await this.connectToSession(qrData, connectionId, options);
          break;
        case 'time_limited_access':
          result = await this.connectTimeLimited(qrData, connectionId, options);
          break;
        case 'multi_service_access':
          result = await this.connectMultiService(qrData, connectionId, options);
          break;
        default:
          result = { success: false, error: `Unsupported connection type: ${qrData.type}` };
      }

      // Update connection status
      connection.status = result.success ? 'connected' : 'failed';
      connection.error = result.error;
      connection.connectedAt = result.success ? Date.now() : undefined;
      
      this.connections.set(connectionId, connection);
      await this.saveConnections();

      // Notify listeners
      this.notifyConnectionChange(connection);

      return { ...result, connectionId };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return { success: false, error: errorMessage };
    }
  }

  /**
   * Connect to tunnel URL
   */
  private async connectToTunnel(
    qrData: QRCodeData,
    connectionId: string,
    options: ConnectionOptions
  ): Promise<ConnectionResult> {
    try {
      if (!qrData.tunnelUrl) {
        return { success: false, error: 'No tunnel URL provided' };
      }

      // Check if URL is reachable
      const testResponse = await fetch(qrData.tunnelUrl, {
        method: 'HEAD',
        timeout: options.timeout || 10000,
      });

      if (!testResponse.ok) {
        return { success: false, error: 'Tunnel URL is not reachable' };
      }

      // Store connection info
      await AsyncStorage.setItem(`connection_${connectionId}`, JSON.stringify({
        type: 'tunnel',
        url: qrData.tunnelUrl,
        serviceName: qrData.serviceName,
        sessionId: qrData.sessionId,
        connectedAt: Date.now(),
      }));

      // Open URL
      const supported = await Linking.canOpenURL(qrData.tunnelUrl);
      if (supported) {
        await Linking.openURL(qrData.tunnelUrl);
        return { success: true, data: { url: qrData.tunnelUrl } };
      } else {
        return { success: false, error: 'Cannot open tunnel URL' };
      }
    } catch (error) {
      return { success: false, error: `Tunnel connection failed: ${error}` };
    }
  }

  /**
   * Connect to mobile app
   */
  private async connectToMobileApp(
    qrData: QRCodeData,
    connectionId: string,
    options: ConnectionOptions
  ): Promise<ConnectionResult> {
    try {
      // Try deep link first
      if (qrData.deepLink) {
        const supported = await Linking.canOpenURL(qrData.deepLink);
        if (supported) {
          await Linking.openURL(qrData.deepLink);
          return { success: true, data: { deepLink: qrData.deepLink } };
        }
      }

      // Fallback to app URL
      if (qrData.appUrl) {
        const supported = await Linking.canOpenURL(qrData.appUrl);
        if (supported) {
          await Linking.openURL(qrData.appUrl);
          return { success: true, data: { appUrl: qrData.appUrl } };
        }
      }

      return { success: false, error: 'No valid app URL or deep link available' };
    } catch (error) {
      return { success: false, error: `Mobile app connection failed: ${error}` };
    }
  }

  /**
   * Connect to session
   */
  private async connectToSession(
    qrData: QRCodeData,
    connectionId: string,
    options: ConnectionOptions
  ): Promise<ConnectionResult> {
    try {
      // Store session data
      const sessionData = {
        sessionId: qrData.sessionId,
        token: qrData.token,
        connectionId,
        connectedAt: Date.now(),
        connectionInfo: qrData.connectionInfo,
      };

      await AsyncStorage.setItem('active_session', JSON.stringify(sessionData));
      await AsyncStorage.setItem(`session_${qrData.sessionId}`, JSON.stringify(sessionData));

      // Navigate to appropriate screen (this would be handled by the app's navigation)
      return { success: true, data: sessionData };
    } catch (error) {
      return { success: false, error: `Session connection failed: ${error}` };
    }
  }

  /**
   * Connect with time limit awareness
   */
  private async connectTimeLimited(
    qrData: QRCodeData,
    connectionId: string,
    options: ConnectionOptions
  ): Promise<ConnectionResult> {
    try {
      // First establish the base connection
      const baseResult = await this.connectToTunnel(qrData, connectionId, options);
      
      if (!baseResult.success) {
        return baseResult;
      }

      // Set up expiration monitoring
      if (qrData.expiresAt) {
        const timeRemaining = qrData.expiresAt - Date.now();
        
        if (timeRemaining > 0) {
          // Schedule cleanup
          setTimeout(() => {
            this.cleanupConnection(connectionId);
          }, timeRemaining);

          // Show warning if expiring soon
          if (timeRemaining < 10 * 60 * 1000) { // Less than 10 minutes
            Alert.alert(
              'Time Limited Access',
              `This connection will expire in ${Math.round(timeRemaining / 60000)} minutes.`,
              [{ text: 'OK' }]
            );
          }
        }
      }

      return baseResult;
    } catch (error) {
      return { success: false, error: `Time-limited connection failed: ${error}` };
    }
  }

  /**
   * Connect to multiple services
   */
  private async connectMultiService(
    qrData: QRCodeData,
    connectionId: string,
    options: ConnectionOptions
  ): Promise<ConnectionResult> {
    try {
      // For now, just connect to the primary service
      // In a full implementation, this would show a service selection dialog
      return await this.connectToTunnel(qrData, connectionId, options);
    } catch (error) {
      return { success: false, error: `Multi-service connection failed: ${error}` };
    }
  }

  /**
   * Get active connections
   */
  getActiveConnections(): any[] {
    return Array.from(this.connections.values())
      .filter(conn => conn.status === 'connected');
  }

  /**
   * Get connection by ID
   */
  getConnection(connectionId: string): any | null {
    return this.connections.get(connectionId) || null;
  }

  /**
   * Disconnect from a connection
   */
  async disconnect(connectionId: string): Promise<boolean> {
    try {
      const connection = this.connections.get(connectionId);
      if (!connection) {
        return false;
      }

      // Update status
      connection.status = 'disconnected';
      connection.disconnectedAt = Date.now();
      
      this.connections.set(connectionId, connection);
      await this.saveConnections();

      // Clean up stored data
      await this.cleanupConnection(connectionId);

      // Notify listeners
      this.notifyConnectionChange(connection);

      return true;
    } catch (error) {
      console.error('Disconnect failed:', error);
      return false;
    }
  }

  /**
   * Clean up connection data
   */
  private async cleanupConnection(connectionId: string) {
    try {
      await AsyncStorage.removeItem(`connection_${connectionId}`);
      
      const connection = this.connections.get(connectionId);
      if (connection?.qrData?.sessionId) {
        await AsyncStorage.removeItem(`session_${connection.qrData.sessionId}`);
      }
    } catch (error) {
      console.error('Cleanup failed:', error);
    }
  }

  /**
   * Add connection listener
   */
  addConnectionListener(listener: Function) {
    this.connectionListeners.add(listener);
  }

  /**
   * Remove connection listener
   */
  removeConnectionListener(listener: Function) {
    this.connectionListeners.delete(listener);
  }

  /**
   * Notify connection change
   */
  private notifyConnectionChange(connection: any) {
    this.connectionListeners.forEach(listener => {
      try {
        listener(connection);
      } catch (error) {
        console.error('Connection listener error:', error);
      }
    });
  }

  /**
   * Generate connection QR code data
   */
  generateConnectionQR(connectionInfo: any): QRCodeData {
    return {
      type: 'mobile_connection',
      sessionId: `mobile_${Date.now()}`,
      serviceName: 'Claude Code Mobile',
      description: 'Connect to Claude Code mobile app',
      expiresAt: Date.now() + (24 * 60 * 60 * 1000), // 24 hours
      connectionInfo,
      deepLink: `claudecode://connect?data=${encodeURIComponent(JSON.stringify(connectionInfo))}`,
    };
  }

  /**
   * Clear all connections
   */
  async clearAllConnections(): Promise<void> {
    try {
      this.connections.clear();
      await AsyncStorage.removeItem('qr_connections');
      await AsyncStorage.removeItem('active_session');
    } catch (error) {
      console.error('Clear connections failed:', error);
    }
  }
}

export default QRConnectionService;