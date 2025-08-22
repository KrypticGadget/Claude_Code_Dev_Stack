/**
 * Deep Link Handler for Claude Code Mobile App
 * Handles deep links from QR codes and external sources
 */

import { Linking, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import QRConnectionService from '../services/QRConnectionService';

interface DeepLinkData {
  scheme: string;
  path: string;
  params: Record<string, string>;
}

interface DeepLinkHandler {
  onConnect?: (connectionData: any) => void;
  onSession?: (sessionData: any) => void;
  onInstructions?: (instructionsData: any) => void;
  onMultiService?: (servicesData: any) => void;
  onError?: (error: string) => void;
}

class DeepLinkManager {
  private connectionService: QRConnectionService;
  private handlers: DeepLinkHandler = {};
  private isListening = false;

  constructor() {
    this.connectionService = new QRConnectionService();
  }

  /**
   * Initialize deep link listening
   */
  initialize(handlers: DeepLinkHandler): void {
    this.handlers = handlers;

    if (!this.isListening) {
      // Handle initial URL (when app is opened from a deep link)
      this.handleInitialURL();

      // Listen for incoming deep links (when app is already running)
      Linking.addEventListener('url', this.handleIncomingURL);
      this.isListening = true;
    }
  }

  /**
   * Clean up listeners
   */
  cleanup(): void {
    if (this.isListening) {
      Linking.removeAllListeners('url');
      this.isListening = false;
    }
  }

  /**
   * Handle initial URL when app opens
   */
  private async handleInitialURL(): Promise<void> {
    try {
      const url = await Linking.getInitialURL();
      if (url) {
        this.processDeepLink(url);
      }
    } catch (error) {
      console.error('Error handling initial URL:', error);
    }
  }

  /**
   * Handle incoming URLs when app is running
   */
  private handleIncomingURL = (event: { url: string }): void => {
    this.processDeepLink(event.url);
  };

  /**
   * Process a deep link URL
   */
  private async processDeepLink(url: string): Promise<void> {
    try {
      const linkData = this.parseDeepLink(url);
      
      if (!linkData) {
        this.handlers.onError?.('Invalid deep link format');
        return;
      }

      // Store the deep link for debugging
      await AsyncStorage.setItem('lastDeepLink', JSON.stringify({
        url,
        parsedData: linkData,
        timestamp: Date.now()
      }));

      // Route based on path
      switch (linkData.path) {
        case 'connect':
          await this.handleConnect(linkData.params);
          break;
        case 'session':
          await this.handleSession(linkData.params);
          break;
        case 'instructions':
          await this.handleInstructions(linkData.params);
          break;
        case 'multiservice':
          await this.handleMultiService(linkData.params);
          break;
        case 'mobile':
          await this.handleMobileAccess(linkData.params);
          break;
        case 'access':
          await this.handleTimeLimitedAccess(linkData.params);
          break;
        default:
          this.handlers.onError?.(`Unknown deep link path: ${linkData.path}`);
      }
    } catch (error) {
      console.error('Deep link processing error:', error);
      this.handlers.onError?.('Failed to process deep link');
    }
  }

  /**
   * Parse deep link URL into components
   */
  private parseDeepLink(url: string): DeepLinkData | null {
    try {
      const urlObj = new URL(url);
      
      // Expected format: claudecode://path?param1=value1&param2=value2
      if (urlObj.protocol !== 'claudecode:') {
        return null;
      }

      const path = urlObj.hostname || urlObj.pathname.replace('/', '');
      const params: Record<string, string> = {};

      urlObj.searchParams.forEach((value, key) => {
        params[key] = value;
      });

      return {
        scheme: urlObj.protocol,
        path,
        params
      };
    } catch (error) {
      console.error('URL parsing error:', error);
      return null;
    }
  }

  /**
   * Handle connection deep link
   */
  private async handleConnect(params: Record<string, string>): Promise<void> {
    try {
      const { token, data } = params;

      if (token) {
        // Validate token and establish connection
        const validation = await this.connectionService.validateQRCode({ 
          type: 'token_access',
          sessionId: `deeplink_${Date.now()}`,
          token 
        });

        if (validation.valid) {
          const connectionResult = await this.connectionService.processQRCode({
            type: 'tunnel_access',
            sessionId: `deeplink_${Date.now()}`,
            token,
            serviceName: 'Claude Code',
            description: 'Deep link connection'
          });

          if (connectionResult.success) {
            this.handlers.onConnect?.(connectionResult);
          } else {
            this.handlers.onError?.(connectionResult.error || 'Connection failed');
          }
        } else {
          this.handlers.onError?.(validation.error || 'Invalid token');
        }
      } else if (data) {
        // Parse embedded connection data
        try {
          const connectionData = JSON.parse(decodeURIComponent(data));
          this.handlers.onConnect?.(connectionData);
        } catch (error) {
          this.handlers.onError?('Invalid connection data format');
        }
      } else {
        this.handlers.onError?('Missing connection parameters');
      }
    } catch (error) {
      this.handlers.onError?.('Connection processing failed');
    }
  }

  /**
   * Handle session deep link
   */
  private async handleSession(params: Record<string, string>): Promise<void> {
    try {
      const { token, session } = params;

      if (token) {
        // Validate session token
        const validation = await this.connectionService.validateQRCode({
          type: 'session_access',
          sessionId: session || `session_${Date.now()}`,
          token
        });

        if (validation.valid) {
          const sessionData = {
            sessionId: session,
            token,
            connectedAt: Date.now(),
            source: 'deeplink'
          };

          await AsyncStorage.setItem('active_session', JSON.stringify(sessionData));
          this.handlers.onSession?.(sessionData);
        } else {
          this.handlers.onError?.(validation.error || 'Invalid session token');
        }
      } else {
        this.handlers.onError?('Missing session token');
      }
    } catch (error) {
      this.handlers.onError?.('Session processing failed');
    }
  }

  /**
   * Handle instructions deep link
   */
  private async handleInstructions(params: Record<string, string>): Promise<void> {
    try {
      const { session, instructions } = params;

      if (session) {
        // Get session instructions
        const instructionsData = instructions ? 
          JSON.parse(decodeURIComponent(instructions)) : 
          { session, defaultInstructions: true };

        this.handlers.onInstructions?.(instructionsData);
      } else {
        this.handlers.onError?('Missing session ID for instructions');
      }
    } catch (error) {
      this.handlers.onError?.('Instructions processing failed');
    }
  }

  /**
   * Handle multi-service deep link
   */
  private async handleMultiService(params: Record<string, string>): Promise<void> {
    try {
      const { token, services } = params;

      if (token) {
        const validation = await this.connectionService.validateQRCode({
          type: 'multi_service_access',
          sessionId: `multiservice_${Date.now()}`,
          token
        });

        if (validation.valid) {
          const servicesData = services ? 
            JSON.parse(decodeURIComponent(services)) : 
            [];

          this.handlers.onMultiService?.({
            token,
            services: servicesData,
            sessionId: `multiservice_${Date.now()}`
          });
        } else {
          this.handlers.onError?.(validation.error || 'Invalid multi-service token');
        }
      } else {
        this.handlers.onError?('Missing multi-service token');
      }
    } catch (error) {
      this.handlers.onError?.('Multi-service processing failed');
    }
  }

  /**
   * Handle mobile access deep link
   */
  private async handleMobileAccess(params: Record<string, string>): Promise<void> {
    try {
      const { token, appUrl } = params;

      const connectionData = {
        type: 'mobile_access',
        sessionId: `mobile_${Date.now()}`,
        token,
        appUrl,
        connectedAt: Date.now()
      };

      if (token) {
        const validation = await this.connectionService.validateQRCode(connectionData);
        if (!validation.valid) {
          this.handlers.onError?.(validation.error || 'Invalid mobile access token');
          return;
        }
      }

      this.handlers.onConnect?.(connectionData);
    } catch (error) {
      this.handlers.onError?.('Mobile access processing failed');
    }
  }

  /**
   * Handle time-limited access deep link
   */
  private async handleTimeLimitedAccess(params: Record<string, string>): Promise<void> {
    try {
      const { token, expires } = params;

      if (token) {
        const expirationTime = expires ? parseInt(expires) : Date.now() + (60 * 60 * 1000); // 1 hour default
        
        const connectionData = {
          type: 'time_limited_access',
          sessionId: `timelimited_${Date.now()}`,
          token,
          expiresAt: expirationTime
        };

        const validation = await this.connectionService.validateQRCode(connectionData);
        
        if (validation.valid) {
          // Check if still valid
          if (Date.now() > expirationTime) {
            this.handlers.onError?('Access link has expired');
            return;
          }

          const connectionResult = await this.connectionService.processQRCode(connectionData);
          
          if (connectionResult.success) {
            this.handlers.onConnect?.(connectionResult);
            
            // Show expiration warning if needed
            const timeRemaining = expirationTime - Date.now();
            if (timeRemaining < 10 * 60 * 1000) { // Less than 10 minutes
              Alert.alert(
                'Time Limited Access',
                `This access will expire in ${Math.round(timeRemaining / 60000)} minutes.`,
                [{ text: 'OK' }]
              );
            }
          } else {
            this.handlers.onError?.(connectionResult.error || 'Connection failed');
          }
        } else {
          this.handlers.onError?.(validation.error || 'Invalid access token');
        }
      } else {
        this.handlers.onError?('Missing access token');
      }
    } catch (error) {
      this.handlers.onError?.('Time-limited access processing failed');
    }
  }

  /**
   * Generate deep link URL
   */
  generateDeepLink(path: string, params: Record<string, string>): string {
    const url = new URL(`claudecode://${path}`);
    
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });

    return url.toString();
  }

  /**
   * Test if deep link can be opened
   */
  async canOpenDeepLink(url: string): Promise<boolean> {
    try {
      return await Linking.canOpenURL(url);
    } catch (error) {
      return false;
    }
  }

  /**
   * Open external URL with fallback
   */
  async openURL(url: string, fallbackUrl?: string): Promise<boolean> {
    try {
      const canOpen = await Linking.canOpenURL(url);
      if (canOpen) {
        await Linking.openURL(url);
        return true;
      } else if (fallbackUrl) {
        const canOpenFallback = await Linking.canOpenURL(fallbackUrl);
        if (canOpenFallback) {
          await Linking.openURL(fallbackUrl);
          return true;
        }
      }
      return false;
    } catch (error) {
      console.error('Error opening URL:', error);
      return false;
    }
  }
}

export default DeepLinkManager;