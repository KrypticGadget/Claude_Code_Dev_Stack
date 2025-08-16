/**
 * Ultimate Statusline View for Mobile
 * 
 * Displays combined statusline from:
 * - Claude Powerline (@Owloops) - Cost/Git/Model tracking
 * - Dev Stack monitoring (Zach) - Agent/Task/Hook orchestration
 * 
 * Real-time updates via WebSocket from statusline bridge
 */

import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';

interface PowerlineData {
  directory: string;
  git: {
    branch: string;
    dirty: boolean;
    ahead: number;
    behind: number;
  };
  model: {
    id: string;
    displayName: string;
  };
  cost: {
    session: number;
    today: number;
    budget: number;
  };
}

interface DevStackMetrics {
  agents: {
    active: number;
    total: number;
    status: 'idle' | 'working' | 'error';
  };
  tasks: {
    active: number;
    completed: number;
    total: number;
    status: 'none' | 'running' | 'complete';
  };
  hooks: {
    triggered: number;
    total: number;
    errors: number;
    status: 'ready' | 'busy' | 'error';
  };
  audio: {
    enabled: boolean;
    volume: number;
    lastEvent: string;
    status: 'silent' | 'playing' | 'error';
  };
}

interface StatuslineData {
  powerline: PowerlineData;
  devStack: DevStackMetrics;
  timestamp: number;
  attribution?: {
    powerline: string;
    devStack: string;
    browser: string;
  };
}

const UltimateStatuslineView: React.FC = () => {
  const [statusData, setStatusData] = useState<StatuslineData | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const [expanded, setExpanded] = useState(false);

  // WebSocket connection management
  const connectWebSocket = useCallback(() => {
    if (websocket?.readyState === WebSocket.OPEN) return;

    setConnectionStatus('connecting');

    const ws = new WebSocket('ws://localhost:8086');

    ws.onopen = () => {
      console.log('Statusline WebSocket connected');
      setConnectionStatus('connected');
      setWebsocket(ws);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'statusline_update' || data.data) {
          setStatusData(data.data || data);
        }
      } catch (error) {
        console.error('Failed to parse statusline data:', error);
      }
    };

    ws.onclose = () => {
      console.log('Statusline WebSocket disconnected');
      setConnectionStatus('disconnected');
      setWebsocket(null);
      
      // Reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
      console.error('Statusline WebSocket error:', error);
      setConnectionStatus('disconnected');
    };

  }, [websocket]);

  // Focus effect to connect when component is focused
  useFocusEffect(
    useCallback(() => {
      connectWebSocket();

      return () => {
        if (websocket) {
          websocket.close();
          setWebsocket(null);
        }
      };
    }, [connectWebSocket])
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [websocket]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'working':
      case 'running':
      case 'busy':
        return '#48bb78'; // Green
      case 'error':
        return '#fc8181'; // Red
      case 'playing':
        return '#f6ad55'; // Orange
      default:
        return '#718096'; // Gray
    }
  };

  const getConnectionIndicator = () => {
    const color = connectionStatus === 'connected' ? '#48bb78' : 
                  connectionStatus === 'connecting' ? '#f6ad55' : '#fc8181';
    return (
      <View style={[styles.connectionIndicator, { backgroundColor: color }]} />
    );
  };

  if (!statusData) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          {getConnectionIndicator()}
          <Text style={styles.headerText}>Connecting to statusline...</Text>
        </View>
      </View>
    );
  }

  const { powerline, devStack } = statusData;

  return (
    <View style={styles.container}>
      {/* Connection Status & Header */}
      <TouchableOpacity 
        style={styles.header}
        onPress={() => setExpanded(!expanded)}
      >
        {getConnectionIndicator()}
        <Text style={styles.headerText}>
          Ultimate Statusline {expanded ? '▼' : '▶'}
        </Text>
        <Text style={styles.timestamp}>
          {new Date(statusData.timestamp).toLocaleTimeString()}
        </Text>
      </TouchableOpacity>

      {/* Compact View */}
      <View style={styles.compactView}>
        {/* Line 1: Powerline (@Owloops) */}
        <View style={styles.statusLine}>
          <Text style={styles.sectionLabel}>Claude Powerline (@Owloops)</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <View style={styles.segmentContainer}>
              <View style={[styles.segment, { backgroundColor: '#1a1b26' }]}>
                <Text style={styles.segmentIcon}>📁</Text>
                <Text style={[styles.segmentText, { color: '#7aa2f7' }]}>
                  {powerline.directory}
                </Text>
              </View>
              
              <View style={[styles.segment, { backgroundColor: '#24283b' }]}>
                <Text style={styles.segmentIcon}>🌿</Text>
                <Text style={[styles.segmentText, { color: '#9ece6a' }]}>
                  {powerline.git.branch}{powerline.git.dirty ? '*' : ''}
                </Text>
              </View>
              
              <View style={[styles.segment, { backgroundColor: '#414868' }]}>
                <Text style={styles.segmentIcon}>🤖</Text>
                <Text style={[styles.segmentText, { color: '#e0af68' }]}>
                  {powerline.model.displayName}
                </Text>
              </View>
              
              <View style={[styles.segment, { backgroundColor: '#565f89' }]}>
                <Text style={styles.segmentIcon}>💵</Text>
                <Text style={[styles.segmentText, { color: '#bb9af7' }]}>
                  ${powerline.cost.session.toFixed(2)}
                </Text>
              </View>
            </View>
          </ScrollView>
        </View>

        {/* Line 2: Dev Stack (Zach) */}
        <View style={styles.statusLine}>
          <Text style={styles.sectionLabel}>Dev Stack Monitoring (Zach)</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <View style={styles.segmentContainer}>
              <View style={[styles.segment, { backgroundColor: '#2d3748' }]}>
                <Text style={styles.segmentIcon}>🤖</Text>
                <Text style={[styles.segmentText, { color: getStatusColor(devStack.agents.status) }]}>
                  {devStack.agents.active}/{devStack.agents.total}
                </Text>
              </View>
              
              <View style={[styles.segment, { backgroundColor: '#2d3748' }]}>
                <Text style={styles.segmentIcon}>⚡</Text>
                <Text style={[styles.segmentText, { color: getStatusColor(devStack.tasks.status) }]}>
                  {devStack.tasks.completed}/{devStack.tasks.total}
                </Text>
              </View>
              
              <View style={[styles.segment, { backgroundColor: '#2d3748' }]}>
                <Text style={styles.segmentIcon}>🔧</Text>
                <Text style={[styles.segmentText, { color: getStatusColor(devStack.hooks.status) }]}>
                  {devStack.hooks.triggered}/{devStack.hooks.total}
                </Text>
              </View>
              
              <View style={[styles.segment, { backgroundColor: '#2d3748' }]}>
                <Text style={styles.segmentIcon}>
                  {devStack.audio.enabled ? '🔊' : '🔇'}
                </Text>
                <Text style={[styles.segmentText, { color: getStatusColor(devStack.audio.status) }]}>
                  {devStack.audio.lastEvent}
                </Text>
              </View>
            </View>
          </ScrollView>
        </View>
      </View>

      {/* Expanded View */}
      {expanded && (
        <View style={styles.expandedView}>
          <Text style={styles.expandedTitle}>Detailed Metrics</Text>
          
          {/* Git Details */}
          <View style={styles.detailSection}>
            <Text style={styles.detailLabel}>Git Status</Text>
            <Text style={styles.detailText}>
              Branch: {powerline.git.branch} {powerline.git.dirty && '(dirty)'}
            </Text>
            {(powerline.git.ahead > 0 || powerline.git.behind > 0) && (
              <Text style={styles.detailText}>
                {powerline.git.ahead > 0 && `↑${powerline.git.ahead} `}
                {powerline.git.behind > 0 && `↓${powerline.git.behind}`}
              </Text>
            )}
          </View>

          {/* Cost Details */}
          <View style={styles.detailSection}>
            <Text style={styles.detailLabel}>Cost Tracking</Text>
            <Text style={styles.detailText}>Session: ${powerline.cost.session.toFixed(2)}</Text>
            <Text style={styles.detailText}>Today: ${powerline.cost.today.toFixed(2)}</Text>
            <Text style={styles.detailText}>Budget: ${powerline.cost.budget.toFixed(2)}</Text>
          </View>

          {/* Agent Details */}
          <View style={styles.detailSection}>
            <Text style={styles.detailLabel}>Agent Orchestration</Text>
            <Text style={styles.detailText}>Active: {devStack.agents.active}</Text>
            <Text style={styles.detailText}>Total: {devStack.agents.total}</Text>
            <Text style={[styles.detailText, { color: getStatusColor(devStack.agents.status) }]}>
              Status: {devStack.agents.status}
            </Text>
          </View>

          {/* Attribution */}
          {statusData.attribution && (
            <View style={styles.attributionSection}>
              <Text style={styles.attributionTitle}>Attribution</Text>
              <Text style={styles.attributionText}>
                Powerline: {statusData.attribution.powerline}
              </Text>
              <Text style={styles.attributionText}>
                Dev Stack: {statusData.attribution.devStack}
              </Text>
              <Text style={styles.attributionText}>
                Browser: {statusData.attribution.browser}
              </Text>
            </View>
          )}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1a1b26',
    borderRadius: 8,
    margin: 8,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#24283b',
    borderBottomWidth: 1,
    borderBottomColor: '#414868',
  },
  connectionIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  headerText: {
    color: '#c0caf5',
    fontSize: 14,
    fontWeight: '600',
    flex: 1,
  },
  timestamp: {
    color: '#565f89',
    fontSize: 12,
  },
  compactView: {
    padding: 8,
  },
  statusLine: {
    marginBottom: 8,
  },
  sectionLabel: {
    color: '#9aa5ce',
    fontSize: 11,
    marginBottom: 4,
    fontStyle: 'italic',
  },
  segmentContainer: {
    flexDirection: 'row',
  },
  segment: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginRight: 1,
    minWidth: 60,
  },
  segmentIcon: {
    fontSize: 12,
    marginRight: 4,
  },
  segmentText: {
    fontSize: 11,
    fontWeight: '500',
    flex: 1,
  },
  expandedView: {
    padding: 12,
    backgroundColor: '#1f2335',
    borderTopWidth: 1,
    borderTopColor: '#414868',
  },
  expandedTitle: {
    color: '#c0caf5',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },
  detailSection: {
    marginBottom: 12,
    padding: 8,
    backgroundColor: '#24283b',
    borderRadius: 4,
  },
  detailLabel: {
    color: '#7aa2f7',
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 4,
  },
  detailText: {
    color: '#c0caf5',
    fontSize: 11,
    marginBottom: 2,
  },
  attributionSection: {
    marginTop: 8,
    padding: 8,
    backgroundColor: '#2d3748',
    borderRadius: 4,
  },
  attributionTitle: {
    color: '#f7768e',
    fontSize: 11,
    fontWeight: '600',
    marginBottom: 4,
  },
  attributionText: {
    color: '#9aa5ce',
    fontSize: 10,
    marginBottom: 1,
  },
});

export default UltimateStatuslineView;