/**
 * QR Code Dashboard Component
 * Manages multiple QR codes for different services and tunnels
 */

import React, { useState, useEffect, useCallback } from 'react';
import QRCodeGenerator from './QRCodeGenerator';
import {
  Plus,
  Trash2,
  RefreshCw,
  Download,
  Settings,
  Globe,
  Smartphone,
  Clock,
  Users,
  BarChart3,
  Filter,
  Search,
  Grid,
  List,
  ChevronDown,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface QRCodeItem {
  id: string;
  type: string;
  name: string;
  data: any;
  qrData?: any;
  createdAt: number;
  expiresAt: number;
  status: 'active' | 'expired' | 'error';
  usage: number;
}

interface TunnelInfo {
  url: string;
  name: string;
  port: number;
  protocol: string;
}

interface QRCodeDashboardProps {
  tunnels?: TunnelInfo[];
  onTunnelChange?: (tunnels: TunnelInfo[]) => void;
}

const QRCodeDashboard: React.FC<QRCodeDashboardProps> = ({
  tunnels = [],
  onTunnelChange
}) => {
  const [qrCodes, setQRCodes] = useState<QRCodeItem[]>([]);
  const [selectedType, setSelectedType] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [stats, setStats] = useState({
    totalActive: 0,
    expiringSoon: 0,
    totalGenerated: 0,
    byType: {} as Record<string, number>
  });

  // QR Code types and their configurations
  const qrCodeTypes = [
    {
      id: 'tunnel',
      name: 'Tunnel Access',
      icon: Globe,
      description: 'QR codes for NGROK tunnels',
      color: 'blue'
    },
    {
      id: 'mobile_access',
      name: 'Mobile App',
      icon: Smartphone,
      description: 'Mobile app access QR codes',
      color: 'green'
    },
    {
      id: 'session',
      name: 'Session Access',
      icon: Users,
      description: 'Session-specific QR codes',
      color: 'purple'
    },
    {
      id: 'time_limited',
      name: 'Time Limited',
      icon: Clock,
      description: 'Temporary access QR codes',
      color: 'orange'
    },
    {
      id: 'multi_service',
      name: 'Multi-Service',
      icon: Grid,
      description: 'Multiple services access',
      color: 'indigo'
    }
  ];

  // Load QR codes and statistics
  const loadData = useCallback(async () => {
    try {
      const [qrResponse, statsResponse] = await Promise.all([
        fetch('/api/qr/list'),
        fetch('/api/qr/stats')
      ]);

      if (qrResponse.ok) {
        const qrData = await qrResponse.json();
        setQRCodes(qrData);
      }

      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }
    } catch (error) {
      console.error('Failed to load QR codes:', error);
    }
  }, []);

  // Auto-refresh data
  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [loadData]);

  // Filter QR codes
  const filteredQRCodes = qrCodes.filter(qr => {
    const matchesType = selectedType === 'all' || qr.type === selectedType;
    const matchesSearch = qr.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesType && matchesSearch;
  });

  // Create new QR code
  const createQRCode = async (type: string, config: any) => {
    try {
      const response = await fetch('/api/qr/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, ...config })
      });

      if (response.ok) {
        const newQR = await response.json();
        setQRCodes(prev => [...prev, newQR]);
        setShowCreateDialog(false);
      }
    } catch (error) {
      console.error('Failed to create QR code:', error);
    }
  };

  // Delete QR code
  const deleteQRCode = async (id: string) => {
    try {
      const response = await fetch(`/api/qr/${id}`, { method: 'DELETE' });
      if (response.ok) {
        setQRCodes(prev => prev.filter(qr => qr.id !== id));
      }
    } catch (error) {
      console.error('Failed to delete QR code:', error);
    }
  };

  // Download all QR codes
  const downloadAllQRCodes = async () => {
    try {
      const response = await fetch('/api/qr/download-batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ qrCodes: filteredQRCodes.map(qr => qr.id) })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `claude-code-qr-codes-${Date.now()}.zip`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Failed to download QR codes:', error);
    }
  };

  // Auto-generate tunnel QR codes
  const generateTunnelQRCodes = async () => {
    for (const tunnel of tunnels) {
      const existingQR = qrCodes.find(qr => 
        qr.type === 'tunnel' && qr.data?.tunnelUrl === tunnel.url
      );

      if (!existingQR) {
        await createQRCode('tunnel', {
          name: `${tunnel.name} Tunnel`,
          data: {
            tunnelUrl: tunnel.url,
            serviceName: tunnel.name,
            description: `Access ${tunnel.name} via tunnel on port ${tunnel.port}`
          }
        });
      }
    }
  };

  // Status icon component
  const StatusIcon = ({ status }: { status: string }) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'expired':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  // QR Code card component
  const QRCodeCard = ({ qr }: { qr: QRCodeItem }) => {
    const typeConfig = qrCodeTypes.find(t => t.id === qr.type);
    const IconComponent = typeConfig?.icon || Globe;

    return (
      <div className="bg-white rounded-lg shadow border hover:shadow-md transition-shadow">
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <IconComponent className={`h-5 w-5 text-${typeConfig?.color}-500 mr-2`} />
              <h3 className="font-medium text-gray-900 truncate">{qr.name}</h3>
            </div>
            <div className="flex items-center space-x-1">
              <StatusIcon status={qr.status} />
              <button
                onClick={() => deleteQRCode(qr.id)}
                className="p-1 text-gray-400 hover:text-red-500 transition-colors"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>

          {qr.qrData && (
            <div className="flex justify-center mb-3">
              <div className="w-32 h-32 bg-gray-50 rounded border flex items-center justify-center">
                <img 
                  src={qr.qrData.qrCode} 
                  alt="QR Code"
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
          )}

          <div className="text-xs text-gray-500 space-y-1">
            <div>Type: {typeConfig?.name}</div>
            <div>Created: {new Date(qr.createdAt).toLocaleDateString()}</div>
            <div>Expires: {new Date(qr.expiresAt).toLocaleDateString()}</div>
            <div>Usage: {qr.usage} scans</div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">QR Code Dashboard</h1>
          <p className="text-gray-600">Manage mobile access QR codes</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={generateTunnelQRCodes}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center"
          >
            <Globe className="h-4 w-4 mr-2" />
            Generate Tunnel QRs
          </button>
          <button
            onClick={() => setShowCreateDialog(true)}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create QR Code
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Active QR Codes</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalActive}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-orange-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Expiring Soon</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.expiringSoon}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <BarChart3 className="h-8 w-8 text-blue-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Generated</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalGenerated}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <Globe className="h-8 w-8 text-purple-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Active Tunnels</p>
              <p className="text-2xl font-semibold text-gray-900">{tunnels.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search QR codes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Types</option>
              {qrCodeTypes.map(type => (
                <option key={type.id} value={type.id}>{type.name}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
              className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
            >
              {viewMode === 'grid' ? <List className="h-4 w-4" /> : <Grid className="h-4 w-4" />}
            </button>

            <button
              onClick={downloadAllQRCodes}
              className="px-3 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors flex items-center"
            >
              <Download className="h-4 w-4 mr-2" />
              Download All
            </button>

            <button
              onClick={loadData}
              className="px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* QR Codes Grid/List */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredQRCodes.map(qr => (
            <QRCodeCard key={qr.id} qr={qr} />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Expires
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Usage
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredQRCodes.map(qr => {
                  const typeConfig = qrCodeTypes.find(t => t.id === qr.type);
                  return (
                    <tr key={qr.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {qr.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {typeConfig?.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <StatusIcon status={qr.status} />
                          <span className="ml-2 text-sm text-gray-500 capitalize">
                            {qr.status}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(qr.createdAt).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(qr.expiresAt).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {qr.usage}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => deleteQRCode(qr.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {filteredQRCodes.length === 0 && (
        <div className="text-center py-12">
          <Grid className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No QR codes found</h3>
          <p className="text-gray-500 mb-4">
            {searchTerm || selectedType !== 'all' 
              ? 'Try adjusting your search or filters'
              : 'Create your first QR code to get started'
            }
          </p>
          <button
            onClick={() => setShowCreateDialog(true)}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Create QR Code
          </button>
        </div>
      )}
    </div>
  );
};

export default QRCodeDashboard;