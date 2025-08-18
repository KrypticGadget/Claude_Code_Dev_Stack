/**
 * MCP Manager Mobile API Bridge
 * React Native integration for MCP service management
 * 
 * Original concept by @qdhenry (MIT License)
 * Enhanced for Claude Code Dev Stack by DevOps Agent
 */

import { NativeModules, NativeEventEmitter, Platform } from 'react-native';

// Service types enum
export enum MCPServiceType {
  CORE = 'core',
  PLAYWRIGHT = 'playwright',
  GITHUB = 'github',
  WEBSEARCH = 'websearch',
  CUSTOM = 'custom',
  PROXY = 'proxy',
  GATEWAY = 'gateway'
}

// Service status enum
export enum MCPServiceStatus {
  STARTING = 'starting',
  RUNNING = 'running',
  STOPPED = 'stopped',
  ERROR = 'error',
  UNKNOWN = 'unknown'
}

// Interfaces
export interface MCPServiceMetrics {
  requestsTotal: number;
  requestsPerSecond: number;
  errorCount: number;
  responseTimeAvg: number;
  cpuUsage: number;
  memoryUsage: number;
  uptime: number; // in seconds
  lastHealthCheck?: string;
}

export interface MCPService {
  id: string;
  name: string;
  serviceType: MCPServiceType;
  host: string;
  port: number;
  path: string;
  protocol: string;
  status: MCPServiceStatus;
  version: string;
  description: string;
  tags: string[];
  metadata: Record<string, any>;
  metrics: MCPServiceMetrics;
  lastSeen?: string;
  healthCheckUrl?: string;
  startupCommand?: string;
  url: string;
  isHealthy: boolean;
}

export interface MCPServiceConfig {
  name: string;
  type: MCPServiceType;
  host?: string;
  port: number;
  path?: string;
  protocol?: string;
  description?: string;
  tags?: string[];
  metadata?: Record<string, any>;
  healthCheckUrl?: string;
  startupCommand?: string;
}

export interface MCPManagerStatus {
  totalServices: number;
  statusBreakdown: Record<string, number>;
  healthyServices: number;
  serviceTypes: string[];
}

export interface MCPManagerConfig {
  healthCheckInterval: number;
  loadBalancing: {
    defaultAlgorithm: string;
    healthCheckTimeout: number;
  };
  logging: {
    level: string;
    file: string;
  };
}

// Events
export type MCPManagerEvent = 
  | 'serviceRegistered'
  | 'serviceUnregistered'
  | 'serviceStatusChanged'
  | 'healthCheckFailed'
  | 'managerStarted'
  | 'managerStopped';

export interface MCPEventData {
  event: MCPManagerEvent;
  service?: MCPService;
  data?: any;
  timestamp: string;
}

// Native module interface
interface MCPManagerNativeModule {
  // Manager lifecycle
  initialize(config?: MCPManagerConfig): Promise<boolean>;
  start(): Promise<boolean>;
  stop(): Promise<boolean>;
  isRunning(): Promise<boolean>;
  
  // Service management
  getServices(filter?: { type?: string; status?: string }): Promise<MCPService[]>;
  getService(serviceId: string): Promise<MCPService | null>;
  getServiceStatus(): Promise<MCPManagerStatus>;
  
  // Service operations
  registerService(config: MCPServiceConfig): Promise<boolean>;
  unregisterService(serviceId: string): Promise<boolean>;
  startService(serviceId: string): Promise<boolean>;
  stopService(serviceId: string): Promise<boolean>;
  restartService(serviceId: string): Promise<boolean>;
  
  // Health checks
  checkServiceHealth(serviceId: string): Promise<boolean>;
  checkAllServicesHealth(): Promise<Record<string, boolean>>;
  
  // Load balancing
  getServiceForRequest(serviceType: string, algorithm?: string): Promise<MCPService | null>;
  
  // Configuration
  getConfiguration(): Promise<MCPManagerConfig>;
  updateConfiguration(config: Partial<MCPManagerConfig>): Promise<boolean>;
  exportConfiguration(format?: 'json' | 'yaml'): Promise<string>;
  
  // Discovery
  discoverServices(): Promise<MCPService[]>;
  scanNetworkForServices(): Promise<MCPService[]>;
  
  // Utilities
  testConnection(host: string, port: number): Promise<boolean>;
  getSystemInfo(): Promise<Record<string, any>>;
}

// Default native module (for platforms that don't support native modules)
const DefaultMCPManager: MCPManagerNativeModule = {
  async initialize() { return false; },
  async start() { return false; },
  async stop() { return false; },
  async isRunning() { return false; },
  async getServices() { return []; },
  async getService() { return null; },
  async getServiceStatus() { 
    return { totalServices: 0, statusBreakdown: {}, healthyServices: 0, serviceTypes: [] };
  },
  async registerService() { return false; },
  async unregisterService() { return false; },
  async startService() { return false; },
  async stopService() { return false; },
  async restartService() { return false; },
  async checkServiceHealth() { return false; },
  async checkAllServicesHealth() { return {}; },
  async getServiceForRequest() { return null; },
  async getConfiguration() { 
    return { 
      healthCheckInterval: 30, 
      loadBalancing: { defaultAlgorithm: 'round_robin', healthCheckTimeout: 10 },
      logging: { level: 'INFO', file: 'mcp-manager.log' }
    };
  },
  async updateConfiguration() { return false; },
  async exportConfiguration() { return '{}'; },
  async discoverServices() { return []; },
  async scanNetworkForServices() { return []; },
  async testConnection() { return false; },
  async getSystemInfo() { return {}; }
};

// Get native module with fallback
const MCPManagerNative: MCPManagerNativeModule = Platform.select({
  ios: NativeModules.MCPManager || DefaultMCPManager,
  android: NativeModules.MCPManager || DefaultMCPManager,
  default: DefaultMCPManager
});

// Event emitter
const MCPManagerEventEmitter = Platform.select({
  ios: new NativeEventEmitter(NativeModules.MCPManager),
  android: new NativeEventEmitter(NativeModules.MCPManager),
  default: new (class MockEventEmitter {
    addListener() { return { remove: () => {} }; }
    removeAllListeners() {}
  })()
});

/**
 * MCP Manager API class for React Native
 * Provides a comprehensive interface for managing MCP services in mobile applications
 */
class MCPManagerAPI {
  private static instance: MCPManagerAPI;
  private initialized: boolean = false;
  private eventListeners: Map<string, Set<Function>> = new Map();
  
  private constructor() {
    this.setupEventListeners();
  }
  
  static getInstance(): MCPManagerAPI {
    if (!MCPManagerAPI.instance) {
      MCPManagerAPI.instance = new MCPManagerAPI();
    }
    return MCPManagerAPI.instance;
  }
  
  private setupEventListeners() {
    // Setup native event listeners
    const events: MCPManagerEvent[] = [
      'serviceRegistered',
      'serviceUnregistered', 
      'serviceStatusChanged',
      'healthCheckFailed',
      'managerStarted',
      'managerStopped'
    ];
    
    events.forEach(event => {
      MCPManagerEventEmitter.addListener(event, (data: MCPEventData) => {
        this.notifyListeners(event, data);
      });
    });
  }
  
  private notifyListeners(event: MCPManagerEvent, data: MCPEventData) {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(data);
        } catch (error) {
          console.error(`Error in MCP Manager event listener for ${event}:`, error);
        }
      });
    }
  }
  
  // Public API methods
  
  /**
   * Initialize the MCP Manager
   */
  async initialize(config?: MCPManagerConfig): Promise<boolean> {
    try {
      const result = await MCPManagerNative.initialize(config);
      this.initialized = result;
      return result;
    } catch (error) {
      console.error('Failed to initialize MCP Manager:', error);
      return false;
    }
  }
  
  /**
   * Check if MCP Manager is initialized
   */
  isInitialized(): boolean {
    return this.initialized;
  }
  
  /**
   * Start the MCP Manager
   */
  async start(): Promise<boolean> {
    if (!this.initialized) {
      throw new Error('MCP Manager not initialized. Call initialize() first.');
    }
    
    try {
      return await MCPManagerNative.start();
    } catch (error) {
      console.error('Failed to start MCP Manager:', error);
      return false;
    }
  }
  
  /**
   * Stop the MCP Manager
   */
  async stop(): Promise<boolean> {
    try {
      return await MCPManagerNative.stop();
    } catch (error) {
      console.error('Failed to stop MCP Manager:', error);
      return false;
    }
  }
  
  /**
   * Check if MCP Manager is running
   */
  async isRunning(): Promise<boolean> {
    try {
      return await MCPManagerNative.isRunning();
    } catch (error) {
      console.error('Failed to check MCP Manager status:', error);
      return false;
    }
  }
  
  /**
   * Get all registered services
   */
  async getServices(filter?: { type?: MCPServiceType; status?: MCPServiceStatus }): Promise<MCPService[]> {
    try {
      const filterParams = filter ? {
        type: filter.type,
        status: filter.status
      } : undefined;
      
      return await MCPManagerNative.getServices(filterParams);
    } catch (error) {
      console.error('Failed to get services:', error);
      return [];
    }
  }
  
  /**
   * Get a specific service by ID
   */
  async getService(serviceId: string): Promise<MCPService | null> {
    try {
      return await MCPManagerNative.getService(serviceId);
    } catch (error) {
      console.error(`Failed to get service ${serviceId}:`, error);
      return null;
    }
  }
  
  /**
   * Get overall service status summary
   */
  async getServiceStatus(): Promise<MCPManagerStatus> {
    try {
      return await MCPManagerNative.getServiceStatus();
    } catch (error) {
      console.error('Failed to get service status:', error);
      return { totalServices: 0, statusBreakdown: {}, healthyServices: 0, serviceTypes: [] };
    }
  }
  
  /**
   * Register a new service
   */
  async registerService(config: MCPServiceConfig): Promise<boolean> {
    try {
      return await MCPManagerNative.registerService(config);
    } catch (error) {
      console.error('Failed to register service:', error);
      return false;
    }
  }
  
  /**
   * Unregister a service
   */
  async unregisterService(serviceId: string): Promise<boolean> {
    try {
      return await MCPManagerNative.unregisterService(serviceId);
    } catch (error) {
      console.error(`Failed to unregister service ${serviceId}:`, error);
      return false;
    }
  }
  
  /**
   * Start a service
   */
  async startService(serviceId: string): Promise<boolean> {
    try {
      return await MCPManagerNative.startService(serviceId);
    } catch (error) {
      console.error(`Failed to start service ${serviceId}:`, error);
      return false;
    }
  }
  
  /**
   * Stop a service
   */
  async stopService(serviceId: string): Promise<boolean> {
    try {
      return await MCPManagerNative.stopService(serviceId);
    } catch (error) {
      console.error(`Failed to stop service ${serviceId}:`, error);
      return false;
    }
  }
  
  /**
   * Restart a service
   */
  async restartService(serviceId: string): Promise<boolean> {
    try {
      return await MCPManagerNative.restartService(serviceId);
    } catch (error) {
      console.error(`Failed to restart service ${serviceId}:`, error);
      return false;
    }
  }
  
  /**
   * Check health of a specific service
   */
  async checkServiceHealth(serviceId: string): Promise<boolean> {
    try {
      return await MCPManagerNative.checkServiceHealth(serviceId);
    } catch (error) {
      console.error(`Failed to check health of service ${serviceId}:`, error);
      return false;
    }
  }
  
  /**
   * Check health of all services
   */
  async checkAllServicesHealth(): Promise<Record<string, boolean>> {
    try {
      return await MCPManagerNative.checkAllServicesHealth();
    } catch (error) {
      console.error('Failed to check health of all services:', error);
      return {};
    }
  }
  
  /**
   * Get the best service instance for a request using load balancing
   */
  async getServiceForRequest(serviceType: MCPServiceType, algorithm: string = 'round_robin'): Promise<MCPService | null> {
    try {
      return await MCPManagerNative.getServiceForRequest(serviceType, algorithm);
    } catch (error) {
      console.error(`Failed to get service for request (${serviceType}):`, error);
      return null;
    }
  }
  
  /**
   * Get current configuration
   */
  async getConfiguration(): Promise<MCPManagerConfig> {
    try {
      return await MCPManagerNative.getConfiguration();
    } catch (error) {
      console.error('Failed to get configuration:', error);
      return {
        healthCheckInterval: 30,
        loadBalancing: { defaultAlgorithm: 'round_robin', healthCheckTimeout: 10 },
        logging: { level: 'INFO', file: 'mcp-manager.log' }
      };
    }
  }
  
  /**
   * Update configuration
   */
  async updateConfiguration(config: Partial<MCPManagerConfig>): Promise<boolean> {
    try {
      return await MCPManagerNative.updateConfiguration(config);
    } catch (error) {
      console.error('Failed to update configuration:', error);
      return false;
    }
  }
  
  /**
   * Export configuration
   */
  async exportConfiguration(format: 'json' | 'yaml' = 'json'): Promise<string> {
    try {
      return await MCPManagerNative.exportConfiguration(format);
    } catch (error) {
      console.error('Failed to export configuration:', error);
      return '{}';
    }
  }
  
  /**
   * Discover services automatically
   */
  async discoverServices(): Promise<MCPService[]> {
    try {
      return await MCPManagerNative.discoverServices();
    } catch (error) {
      console.error('Failed to discover services:', error);
      return [];
    }
  }
  
  /**
   * Scan network for MCP services
   */
  async scanNetworkForServices(): Promise<MCPService[]> {
    try {
      return await MCPManagerNative.scanNetworkForServices();
    } catch (error) {
      console.error('Failed to scan network for services:', error);
      return [];
    }
  }
  
  /**
   * Test connection to a host/port
   */
  async testConnection(host: string, port: number): Promise<boolean> {
    try {
      return await MCPManagerNative.testConnection(host, port);
    } catch (error) {
      console.error(`Failed to test connection to ${host}:${port}:`, error);
      return false;
    }
  }
  
  /**
   * Get system information
   */
  async getSystemInfo(): Promise<Record<string, any>> {
    try {
      return await MCPManagerNative.getSystemInfo();
    } catch (error) {
      console.error('Failed to get system info:', error);
      return {};
    }
  }
  
  // Event management
  
  /**
   * Add event listener
   */
  addEventListener(event: MCPManagerEvent, listener: (data: MCPEventData) => void): () => void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set());
    }
    
    this.eventListeners.get(event)!.add(listener);
    
    // Return cleanup function
    return () => {
      const listeners = this.eventListeners.get(event);
      if (listeners) {
        listeners.delete(listener);
        if (listeners.size === 0) {
          this.eventListeners.delete(event);
        }
      }
    };
  }
  
  /**
   * Remove all event listeners for a specific event
   */
  removeAllListeners(event?: MCPManagerEvent) {
    if (event) {
      this.eventListeners.delete(event);
    } else {
      this.eventListeners.clear();
    }
  }
}

// React hooks for easier integration

/**
 * React hook for MCP Manager services
 */
export function useMCPServices(filter?: { type?: MCPServiceType; status?: MCPServiceStatus }) {
  const [services, setServices] = React.useState<MCPService[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  
  const refreshServices = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const mcpManager = MCPManagerAPI.getInstance();
      const serviceList = await mcpManager.getServices(filter);
      setServices(serviceList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load services');
    } finally {
      setLoading(false);
    }
  }, [filter]);
  
  React.useEffect(() => {
    refreshServices();
    
    // Setup event listeners for real-time updates
    const mcpManager = MCPManagerAPI.getInstance();
    const listeners = [
      mcpManager.addEventListener('serviceRegistered', refreshServices),
      mcpManager.addEventListener('serviceUnregistered', refreshServices),
      mcpManager.addEventListener('serviceStatusChanged', refreshServices)
    ];
    
    return () => {
      listeners.forEach(cleanup => cleanup());
    };
  }, [refreshServices]);
  
  return { services, loading, error, refreshServices };
}

/**
 * React hook for MCP Manager status
 */
export function useMCPManagerStatus() {
  const [status, setStatus] = React.useState<MCPManagerStatus | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  
  const refreshStatus = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const mcpManager = MCPManagerAPI.getInstance();
      const managerStatus = await mcpManager.getServiceStatus();
      setStatus(managerStatus);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load status');
    } finally {
      setLoading(false);
    }
  }, []);
  
  React.useEffect(() => {
    refreshStatus();
    
    // Refresh every 30 seconds
    const interval = setInterval(refreshStatus, 30000);
    
    return () => clearInterval(interval);
  }, [refreshStatus]);
  
  return { status, loading, error, refreshStatus };
}

// Default export
export default MCPManagerAPI.getInstance();

// Named exports
export { 
  MCPManagerAPI,
  MCPManagerNative,
  MCPManagerEventEmitter 
};