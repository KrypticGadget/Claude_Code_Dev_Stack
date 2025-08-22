/**
 * Mobile-Optimized Landing Page for QR Code Access
 * Handles deep links and provides mobile-friendly interface
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Smartphone,
  Download,
  Globe,
  Shield,
  Clock,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  Copy,
  Share2,
  ArrowRight,
  Wifi,
  Settings,
  Play,
  QrCode
} from 'lucide-react';

interface ConnectionInfo {
  tunnelUrl?: string;
  serviceName?: string;
  description?: string;
  features?: string[];
  instructions?: string[];
  deepLink?: string;
  platformUrls?: {
    ios?: string;
    android?: string;
    web?: string;
  };
}

interface MobileLandingProps {
  className?: string;
}

const MobileLanding: React.FC<MobileLandingProps> = ({ className = '' }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [connectionInfo, setConnectionInfo] = useState<ConnectionInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deviceInfo, setDeviceInfo] = useState({
    isMobile: false,
    isIOS: false,
    isAndroid: false,
    userAgent: ''
  });

  // Detect device information
  useEffect(() => {
    const userAgent = navigator.userAgent;
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
    const isIOS = /iPad|iPhone|iPod/.test(userAgent);
    const isAndroid = /Android/.test(userAgent);

    setDeviceInfo({
      isMobile,
      isIOS,
      isAndroid,
      userAgent
    });
  }, []);

  // Process URL parameters and tokens
  useEffect(() => {
    const processParameters = async () => {
      setLoading(true);
      setError(null);

      try {
        const token = searchParams.get('token');
        const sessionId = searchParams.get('session');
        const action = searchParams.get('action');

        if (token) {
          // Validate token and get connection info
          const response = await fetch('/api/qr/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token })
          });

          if (response.ok) {
            const data = await response.json();
            setConnectionInfo(data.connectionInfo);
          } else {
            setError('Invalid or expired access token');
          }
        } else if (sessionId) {
          // Get session info
          const response = await fetch(`/api/qr/session/${sessionId}`);
          if (response.ok) {
            const data = await response.json();
            setConnectionInfo(data);
          } else {
            setError('Session not found or expired');
          }
        } else {
          // Default connection info
          setConnectionInfo({
            serviceName: 'Claude Code Dev Stack',
            description: 'Connect to Claude Code development environment',
            features: [
              'Real-time WebSocket connection',
              'Mobile-optimized interface',
              'Secure token-based authentication',
              'Cross-platform compatibility'
            ]
          });
        }
      } catch (err) {
        setError('Failed to load connection information');
        console.error('Error processing parameters:', err);
      } finally {
        setLoading(false);
      }
    };

    processParameters();
  }, [searchParams]);

  // Handle app download
  const handleDownload = (platform: 'ios' | 'android' | 'web') => {
    const urls = connectionInfo?.platformUrls || {};
    
    switch (platform) {
      case 'ios':
        window.open(urls.ios || 'https://apps.apple.com/app/claude-code', '_blank');
        break;
      case 'android':
        window.open(urls.android || 'https://play.google.com/store/apps/details?id=com.claudecode', '_blank');
        break;
      case 'web':
        if (connectionInfo?.tunnelUrl) {
          window.open(connectionInfo.tunnelUrl, '_blank');
        } else {
          navigate('/app');
        }
        break;
    }
  };

  // Handle deep link
  const handleDeepLink = () => {
    if (connectionInfo?.deepLink) {
      window.location.href = connectionInfo.deepLink;
      
      // Fallback to app store if deep link fails
      setTimeout(() => {
        if (deviceInfo.isIOS) {
          handleDownload('ios');
        } else if (deviceInfo.isAndroid) {
          handleDownload('android');
        }
      }, 2000);
    }
  };

  // Copy connection URL
  const copyUrl = async () => {
    try {
      await navigator.clipboard.writeText(connectionInfo?.tunnelUrl || window.location.href);
      // Could add toast notification here
    } catch (error) {
      console.error('Failed to copy URL:', error);
    }
  };

  // Share connection
  const shareConnection = async () => {
    if (navigator.share && connectionInfo) {
      try {
        await navigator.share({
          title: connectionInfo.serviceName || 'Claude Code Access',
          text: connectionInfo.description || 'Connect to Claude Code',
          url: connectionInfo.tunnelUrl || window.location.href
        });
      } catch (error) {
        console.error('Failed to share:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className={`min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center ${className}`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading connection information...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center ${className}`}>
        <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Connection Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100 ${className}`}>
      <div className="max-w-lg mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="bg-white rounded-full w-20 h-20 mx-auto mb-4 flex items-center justify-center shadow-lg">
            <QrCode className="h-10 w-10 text-blue-500" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            {connectionInfo?.serviceName || 'Claude Code'}
          </h1>
          <p className="text-gray-600">
            {connectionInfo?.description || 'Mobile access via QR code'}
          </p>
        </div>

        {/* Connection Status */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-center mb-4">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-2"></div>
              <span className="text-sm font-medium text-green-600">Connection Ready</span>
            </div>
          </div>

          {/* Primary Action */}
          {deviceInfo.isMobile ? (
            <div className="space-y-3">
              <button
                onClick={handleDeepLink}
                className="w-full px-6 py-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center font-medium"
              >
                <Play className="h-5 w-5 mr-2" />
                Open in Claude Code App
              </button>
              
              <div className="text-center">
                <span className="text-sm text-gray-500">or</span>
              </div>
              
              <button
                onClick={() => handleDownload('web')}
                className="w-full px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center"
              >
                <Globe className="h-4 w-4 mr-2" />
                Continue in Browser
              </button>
            </div>
          ) : (
            <button
              onClick={() => handleDownload('web')}
              className="w-full px-6 py-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center font-medium"
            >
              <ArrowRight className="h-5 w-5 mr-2" />
              Connect Now
            </button>
          )}
        </div>

        {/* Features */}
        {connectionInfo?.features && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 className="font-semibold text-gray-900 mb-4">Features</h3>
            <div className="space-y-3">
              {connectionInfo.features.map((feature, index) => (
                <div key={index} className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />
                  <span className="text-sm text-gray-600">{feature}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Instructions */}
        {connectionInfo?.instructions && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 className="font-semibold text-gray-900 mb-4">Instructions</h3>
            <div className="space-y-3">
              {connectionInfo.instructions.map((instruction, index) => (
                <div key={index} className="flex">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-medium mr-3">
                    {index + 1}
                  </span>
                  <span className="text-sm text-gray-600">{instruction}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Download Options */}
        {deviceInfo.isMobile && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 className="font-semibold text-gray-900 mb-4">Download App</h3>
            <div className="grid grid-cols-2 gap-3">
              {deviceInfo.isIOS && (
                <button
                  onClick={() => handleDownload('ios')}
                  className="flex items-center justify-center px-4 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors"
                >
                  <Download className="h-4 w-4 mr-2" />
                  <span className="text-sm">App Store</span>
                </button>
              )}
              
              {deviceInfo.isAndroid && (
                <button
                  onClick={() => handleDownload('android')}
                  className="flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Download className="h-4 w-4 mr-2" />
                  <span className="text-sm">Play Store</span>
                </button>
              )}
            </div>
          </div>
        )}

        {/* Connection Info */}
        {connectionInfo?.tunnelUrl && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 className="font-semibold text-gray-900 mb-4">Connection Details</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <Wifi className="h-4 w-4 text-gray-500 mr-2" />
                  <span className="text-sm text-gray-600">Tunnel URL</span>
                </div>
                <button
                  onClick={copyUrl}
                  className="text-blue-500 hover:text-blue-600"
                >
                  <Copy className="h-4 w-4" />
                </button>
              </div>
              
              <div className="text-xs text-gray-500 break-all font-mono bg-gray-50 p-2 rounded">
                {connectionInfo.tunnelUrl}
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex space-x-3">
          <button
            onClick={copyUrl}
            className="flex-1 px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center"
          >
            <Copy className="h-4 w-4 mr-2" />
            Copy URL
          </button>
          
          {navigator.share && (
            <button
              onClick={shareConnection}
              className="flex-1 px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center"
            >
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </button>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-xs text-gray-500">
          <p>Powered by Claude Code Dev Stack v3.6.9</p>
          <p className="mt-1">Secure • Fast • Mobile-Optimized</p>
        </div>
      </div>
    </div>
  );
};

export default MobileLanding;