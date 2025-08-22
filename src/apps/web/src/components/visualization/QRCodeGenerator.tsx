/**
 * QR Code Generator Component for Claude Code Mobile Access
 * React component for displaying and managing QR codes
 */

import React, { useState, useEffect, useCallback } from 'react';
import QRCode from 'react-qr-code';
import { 
  Download, 
  Copy, 
  RefreshCw, 
  Clock, 
  Smartphone, 
  Link, 
  Settings,
  QrCode,
  Share2,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

interface QRCodeData {
  qrCode: string;
  sessionId: string;
  token: string;
  expiresAt: number;
  deepLink?: string;
  type: string;
}

interface QRCodeCustomization {
  size?: number;
  margin?: number;
  color?: {
    dark: string;
    light: string;
  };
  logo?: string;
}

interface QRCodeGeneratorProps {
  type: 'tunnel' | 'mobile_access' | 'session' | 'time_limited' | 'multi_service';
  data: any;
  onGenerate?: (qrData: QRCodeData) => void;
  onError?: (error: string) => void;
  customization?: QRCodeCustomization;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const QRCodeGenerator: React.FC<QRCodeGeneratorProps> = ({
  type,
  data,
  onGenerate,
  onError,
  customization = {},
  autoRefresh = false,
  refreshInterval = 300000 // 5 minutes
}) => {
  const [qrData, setQRData] = useState<QRCodeData | null>(null);
  const [loading, setLoading] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [showToken, setShowToken] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [qrCustomization, setQRCustomization] = useState<QRCodeCustomization>({
    size: 256,
    margin: 4,
    color: {
      dark: '#000000',
      light: '#FFFFFF'
    },
    ...customization
  });

  // Generate QR code
  const generateQRCode = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/qr/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type,
          data,
          customization: qrCustomization
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate QR code: ${response.statusText}`);
      }

      const result = await response.json();
      setQRData(result);
      onGenerate?.(result);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      onError?.(errorMessage);
      console.error('QR code generation error:', error);
    } finally {
      setLoading(false);
    }
  }, [type, data, qrCustomization, onGenerate, onError]);

  // Update time remaining
  useEffect(() => {
    if (!qrData) return;

    const updateTimer = () => {
      const remaining = qrData.expiresAt - Date.now();
      setTimeRemaining(Math.max(0, remaining));
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);

    return () => clearInterval(interval);
  }, [qrData]);

  // Auto refresh
  useEffect(() => {
    if (!autoRefresh || !qrData) return;

    const interval = setInterval(() => {
      if (timeRemaining > 60000) { // Only refresh if more than 1 minute remaining
        generateQRCode();
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, qrData, timeRemaining, generateQRCode]);

  // Initial generation
  useEffect(() => {
    generateQRCode();
  }, [generateQRCode]);

  // Format time remaining
  const formatTimeRemaining = (ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  };

  // Copy to clipboard
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // Could add toast notification here
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  // Download QR code
  const downloadQRCode = () => {
    if (!qrData) return;

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx?.drawImage(img, 0, 0);

      const link = document.createElement('a');
      link.download = `claude-code-qr-${qrData.sessionId}.png`;
      link.href = canvas.toDataURL();
      link.click();
    };

    img.src = qrData.qrCode;
  };

  // Share QR code (if supported)
  const shareQRCode = async () => {
    if (!qrData || !navigator.share) return;

    try {
      await navigator.share({
        title: 'Claude Code Access',
        text: `Access Claude Code via QR code`,
        url: qrData.deepLink || qrData.token
      });
    } catch (error) {
      console.error('Failed to share:', error);
    }
  };

  // Open deep link
  const openDeepLink = () => {
    if (!qrData?.deepLink) return;
    window.open(qrData.deepLink, '_blank');
  };

  if (loading && !qrData) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600">Generating QR code...</span>
      </div>
    );
  }

  if (!qrData) {
    return (
      <div className="text-center p-8">
        <QrCode className="h-12 w-12 mx-auto text-gray-400 mb-4" />
        <p className="text-gray-500">Failed to generate QR code</p>
        <button
          onClick={generateQRCode}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-md mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Mobile Access QR Code
        </h3>
        <div className="flex gap-2">
          <button
            onClick={generateQRCode}
            disabled={loading}
            className="p-2 text-gray-500 hover:text-blue-500 transition-colors"
            title="Refresh QR Code"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="p-2 text-gray-500 hover:text-blue-500 transition-colors"
            title="Advanced Options"
          >
            <Settings className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* QR Code Display */}
      <div className="flex justify-center mb-4">
        <div className="p-4 bg-white rounded-lg border-2 border-gray-200">
          <QRCode
            value={qrData.qrCode}
            size={qrCustomization.size}
            bgColor={qrCustomization.color?.light}
            fgColor={qrCustomization.color?.dark}
          />
        </div>
      </div>

      {/* Time Remaining */}
      <div className="flex items-center justify-center mb-4 p-3 bg-gray-50 rounded-lg">
        <Clock className="h-4 w-4 text-gray-500 mr-2" />
        <span className="text-sm text-gray-600">
          Expires in: <strong className={timeRemaining < 60000 ? 'text-red-500' : 'text-green-500'}>
            {formatTimeRemaining(timeRemaining)}
          </strong>
        </span>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <button
          onClick={downloadQRCode}
          className="flex items-center justify-center px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Download className="h-4 w-4 mr-1" />
          <span className="text-sm">Download</span>
        </button>

        {navigator.share && (
          <button
            onClick={shareQRCode}
            className="flex items-center justify-center px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            <Share2 className="h-4 w-4 mr-1" />
            <span className="text-sm">Share</span>
          </button>
        )}

        {qrData.deepLink && (
          <button
            onClick={openDeepLink}
            className="flex items-center justify-center px-3 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
          >
            <Smartphone className="h-4 w-4 mr-1" />
            <span className="text-sm">Open App</span>
          </button>
        )}

        <button
          onClick={() => copyToClipboard(qrData.deepLink || qrData.token)}
          className="flex items-center justify-center px-3 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
        >
          <Copy className="h-4 w-4 mr-1" />
          <span className="text-sm">Copy Link</span>
        </button>
      </div>

      {/* Token Display */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Access Token</span>
          <button
            onClick={() => setShowToken(!showToken)}
            className="text-xs text-blue-500 hover:text-blue-600 flex items-center"
          >
            {showToken ? <EyeOff className="h-3 w-3 mr-1" /> : <Eye className="h-3 w-3 mr-1" />}
            {showToken ? 'Hide' : 'Show'}
          </button>
        </div>
        <div className="p-2 bg-gray-50 rounded border">
          {showToken ? (
            <code className="text-xs text-gray-600 break-all">{qrData.token}</code>
          ) : (
            <span className="text-xs text-gray-400">••••••••••••••••</span>
          )}
        </div>
      </div>

      {/* Advanced Options */}
      {showAdvanced && (
        <div className="border-t pt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Customization</span>
            <button
              onClick={() => setShowAdvanced(false)}
              className="text-xs text-gray-500"
            >
              <ChevronUp className="h-4 w-4" />
            </button>
          </div>

          <div className="space-y-3">
            {/* Size Control */}
            <div>
              <label className="block text-xs text-gray-600 mb-1">Size</label>
              <input
                type="range"
                min="128"
                max="512"
                step="32"
                value={qrCustomization.size}
                onChange={(e) => setQRCustomization(prev => ({
                  ...prev,
                  size: parseInt(e.target.value)
                }))}
                className="w-full"
              />
              <span className="text-xs text-gray-500">{qrCustomization.size}px</span>
            </div>

            {/* Color Controls */}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs text-gray-600 mb-1">Foreground</label>
                <input
                  type="color"
                  value={qrCustomization.color?.dark}
                  onChange={(e) => setQRCustomization(prev => ({
                    ...prev,
                    color: { ...prev.color!, dark: e.target.value }
                  }))}
                  className="w-full h-8 rounded border"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Background</label>
                <input
                  type="color"
                  value={qrCustomization.color?.light}
                  onChange={(e) => setQRCustomization(prev => ({
                    ...prev,
                    color: { ...prev.color!, light: e.target.value }
                  }))}
                  className="w-full h-8 rounded border"
                />
              </div>
            </div>

            <button
              onClick={generateQRCode}
              className="w-full px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
            >
              Apply Changes
            </button>
          </div>
        </div>
      )}

      {/* Info */}
      <div className="text-xs text-gray-500 text-center mt-4">
        Session ID: {qrData.sessionId.slice(0, 8)}...
        <br />
        Type: {qrData.type.replace('_', ' ')}
      </div>
    </div>
  );
};

export default QRCodeGenerator;