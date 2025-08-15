/**
 * Connection configuration model
 * Ported from Flutter ConnectionConfig model (@9cat) - MIT License
 */

export interface ConnectionConfig {
  serverUrl: string;
  username: string;
  password: string;
  isConnected?: boolean;
}

export class ConnectionConfigImpl implements ConnectionConfig {
  serverUrl: string;
  username: string;
  password: string;
  isConnected: boolean;

  constructor(config: {
    serverUrl: string;
    username: string;
    password: string;
    isConnected?: boolean;
  }) {
    this.serverUrl = config.serverUrl;
    this.username = config.username;
    this.password = config.password;
    this.isConnected = config.isConnected || false;
  }

  copyWith(updates: Partial<ConnectionConfig>): ConnectionConfigImpl {
    return new ConnectionConfigImpl({
      serverUrl: updates.serverUrl ?? this.serverUrl,
      username: updates.username ?? this.username,
      password: updates.password ?? this.password,
      isConnected: updates.isConnected ?? this.isConnected,
    });
  }

  toJson(): Record<string, any> {
    return {
      serverUrl: this.serverUrl,
      username: this.username,
      password: this.password,
      isConnected: this.isConnected,
    };
  }

  static fromJson(json: Record<string, any>): ConnectionConfigImpl {
    return new ConnectionConfigImpl({
      serverUrl: json.serverUrl || '',
      username: json.username || '',
      password: json.password || '',
      isConnected: json.isConnected || false,
    });
  }
}