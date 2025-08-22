# Category 3: Agent Triggers
**Automatic agent activation and coordination**

## Hook Inventory

### Primary Hooks
1. **agent_mention_parser.py** - Parse and track @agent- mention invocations
   - Pattern matching for @agent-[name] mentions
   - Model specification parsing ([opus|haiku])
   - Routing state management
   - Deterministic agent activation

2. **master_orchestrator.py** - Central orchestration and agent coordination
   - Agent workflow orchestration
   - Cross-agent communication
   - Resource allocation management
   - Execution planning

3. **smart_orchestrator.py** - Intelligent agent selection and routing
   - Context-aware agent selection
   - Performance-based routing
   - Load balancing across agents
   - Pattern recognition for optimal routing

4. **orchestration_enhancer.py** - Enhanced orchestration capabilities
   - Advanced coordination patterns
   - Agent capability matching
   - Dynamic workflow adaptation
   - Performance optimization

5. **v3_orchestrator.py** - V3.0+ orchestration features
   - Modern orchestration patterns
   - Enhanced agent protocols
   - Improved error handling
   - Advanced coordination features

6. **parallel_execution_engine.py** - Parallel agent execution management
   - Concurrent agent execution
   - Resource synchronization
   - Dependency resolution
   - Performance optimization

### Supporting Hooks
7. **planning_trigger.py** - Planning and strategy triggering
8. **orchestration_demo.py** - Orchestration demonstration and testing
9. **agent_enhancer_v3.py** - V3.0+ agent enhancement capabilities

## Dependencies

### Direct Dependencies
- **json** for state management and configuration
- **re** for pattern matching and parsing
- **datetime** for timestamp management
- **pathlib** for state file management
- **asyncio** for parallel execution
- **concurrent.futures** for thread/process management

### System Dependencies
- Agent registry and capability database
- State directory (.claude/state)
- Configuration management system
- Inter-process communication mechanisms

## Execution Priority

### Priority 1 (Critical)
1. **agent_mention_parser.py** - Must execute first to detect agent requests
2. **master_orchestrator.py** - Central coordination authority

### Priority 2 (High)
3. **smart_orchestrator.py** - Intelligent routing decisions
4. **v3_orchestrator.py** - Modern orchestration features

### Priority 3 (Standard)
5. **orchestration_enhancer.py** - Enhanced capabilities
6. **parallel_execution_engine.py** - Parallel execution optimization
7. **planning_trigger.py** - Strategic planning
8. **agent_enhancer_v3.py** - Agent enhancement

### Priority 4 (Supporting)
9. **orchestration_demo.py** - Testing and demonstration

## Cross-Category Dependencies

### Upstream Dependencies
- **Authentication** (Category 11): Agent permission validation
- **Session Management** (Category 10): Context and state management
- **Error Handling** (Category 7): Orchestration failure recovery

### Downstream Dependencies
- **All Categories**: Agent triggers coordinate all other categories
- **Performance Monitoring** (Category 8): Orchestration metrics
- **Notification** (Category 12): Agent status updates

## Configuration Template

```json
{
  "agent_triggers": {
    "enabled": true,
    "priority": 1,
    "mention_parsing": {
      "pattern": "@agent-([a-z-]+)(?:\\[(opus|haiku)\\])?",
      "state_retention": 50,
      "auto_routing": true,
      "default_model": "default"
    },
    "orchestration": {
      "max_concurrent_agents": 5,
      "timeout_seconds": 300,
      "retry_attempts": 3,
      "load_balancing": true
    },
    "smart_routing": {
      "context_awareness": true,
      "performance_weighting": 0.7,
      "capability_matching": true,
      "learning_enabled": true
    },
    "parallel_execution": {
      "enabled": true,
      "max_workers": 4,
      "resource_limits": {
        "memory_mb": 1000,
        "cpu_percent": 80
      }
    },
    "agent_registry": {
      "auto_discovery": true,
      "capability_scanning": true,
      "health_monitoring": true
    }
  }
}
```

## Integration Manifest

### Input Interfaces
- **User Input**: @agent- mentions and commands
- **System Events**: Agent registration, capability changes
- **Context Changes**: Session state updates, resource availability

### Output Interfaces
- **Agent Activation**: Direct agent invocation
- **Coordination Events**: Multi-agent workflow coordination
- **Status Updates**: Agent execution status and results

### Communication Protocols
- **Mention Detection**: Real-time parsing of user input
- **Agent Registry**: Dynamic agent capability discovery
- **State Management**: Persistent routing and coordination state
- **Event Bus**: Agent coordination event broadcasting

### Resource Allocation
- **CPU**: High priority for orchestration decisions
- **Memory**: 200-500MB for agent state and coordination
- **Network**: Agent communication and coordination
- **Storage**: State persistence and coordination history

## Agent Coordination Patterns

### Sequential Execution
1. Parse agent mentions in order
2. Execute agents with dependency resolution
3. Chain outputs between dependent agents
4. Aggregate final results

### Parallel Execution
1. Identify independent agent tasks
2. Execute non-dependent agents concurrently
3. Synchronize results and dependencies
4. Merge parallel execution results

### Hierarchical Coordination
1. Master orchestrator oversees execution
2. Sub-orchestrators manage specific domains
3. Agent clusters for related functionality
4. Escalation paths for complex scenarios

## Error Recovery Strategies

### Agent Unavailability
1. Fallback to alternative agents with similar capabilities
2. Queue requests for when agents become available
3. Graceful degradation with reduced functionality
4. User notification of service limitations

### Orchestration Failures
1. Retry with exponential backoff
2. Isolate failing components
3. Continue with available agents
4. Emergency fallback to manual mode

### Resource Exhaustion
1. Queue excess requests
2. Implement priority-based scheduling
3. Resource cleanup and optimization
4. Load shedding for non-critical operations

## Performance Thresholds

### Coordination Limits
- **Agent Activation**: <500ms from mention detection
- **Orchestration Decision**: <1s for routing decisions
- **Parallel Execution**: <10s overhead for coordination

### Resource Limits
- **Concurrent Agents**: 5 maximum by default
- **Memory Usage**: 500MB maximum for orchestration
- **CPU Usage**: 80% maximum for coordination tasks

### Quality Metrics
- **Success Rate**: >98% for agent activation
- **Response Time**: <2s average for coordination
- **Throughput**: >100 agent activations/minute

## Agent Registry Integration

### Capability Discovery
- **Automatic Scanning**: Detect agent capabilities at startup
- **Dynamic Updates**: Real-time capability registration
- **Health Monitoring**: Continuous agent availability checking
- **Performance Tracking**: Agent execution metrics collection

### Routing Optimization
- **Performance Weighting**: Route based on historical performance
- **Capability Matching**: Match requests to best-suited agents
- **Load Balancing**: Distribute load across available agents
- **Context Awareness**: Consider current context for routing

### State Management
- **Persistent State**: Maintain routing decisions and agent history
- **Session Continuity**: Preserve agent context across sessions
- **Recovery State**: Quick recovery from failures
- **Analytics Data**: Performance and usage analytics

## Advanced Coordination Features

### Workflow Orchestration
- **Multi-step Workflows**: Complex agent interaction patterns
- **Conditional Execution**: Dynamic workflow branching
- **Loop Handling**: Iterative agent execution patterns
- **Error Propagation**: Intelligent error handling across workflows

### Real-time Coordination
- **Live Monitoring**: Real-time agent execution monitoring
- **Dynamic Scaling**: Automatic resource allocation adjustment
- **Hot Swapping**: Replace agents without interruption
- **Circuit Breakers**: Prevent cascade failures

### Intelligence Enhancement
- **Learning Algorithms**: Improve routing decisions over time
- **Pattern Recognition**: Identify optimal coordination patterns
- **Predictive Routing**: Anticipate agent needs
- **Adaptive Optimization**: Continuous performance improvement