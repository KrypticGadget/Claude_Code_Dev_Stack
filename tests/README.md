# Comprehensive Agent Test Suite V3.6.9

A comprehensive testing framework for all 37 agents in the V3.6.9 Claude Code Agents system (27 core + 10 BMAD agents).

## 🎯 Overview

This test suite provides complete coverage for:
- **Individual Agent Operations**: Core functionality testing for each agent
- **Inter-Agent Communication**: Handoff protocols and context sharing validation
- **Context Preservation**: Context integrity across agent transitions
- **Error Scenarios**: Failure handling, timeouts, and recovery procedures
- **Performance Benchmarks**: Execution times and resource usage monitoring
- **Load Testing**: Multi-agent workflows under stress conditions
- **Integration Testing**: End-to-end workflow validation

## 📁 Directory Structure

```
tests/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config/
│   └── test-config.yaml              # Test configuration
├── agent-test-framework.py            # Core test framework
├── agent-test-framework-extended.py   # Extended testing capabilities
├── test-runner.py                     # Main test orchestrator
├── ci-cd-integration.py              # CI/CD pipeline integration
├── validate-quality-gates.py         # Quality gate validation
├── logs/                              # Test execution logs
├── reports/                           # Test reports and results
├── data/                              # Test data and fixtures
└── baselines/                         # Performance baselines
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** installed
2. **Git** for version control integration
3. **All 37 agents** properly configured in the system

### Installation

1. **Clone and navigate to the test directory:**
   ```bash
   cd tests/
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify agent discovery:**
   ```bash
   python -c "from agent_test_framework import AgentTestFramework; f = AgentTestFramework(); print(f'Discovered {len(f.agents)} agents')"
   ```

### Running Tests

#### 🎯 Run All Tests
```bash
python test-runner.py
```

#### 🎯 Run Specific Test Suites
```bash
# Individual agent testing
python test-runner.py --suites individual_operations

# Communication and context testing
python test-runner.py --suites inter_agent_communication context_preservation

# Performance and load testing
python test-runner.py --suites performance_benchmarks load_testing

# Complete integration testing
python test-runner.py --suites integration_testing
```

#### 🎯 Verbose Output
```bash
python test-runner.py --verbose
```

#### 🎯 Custom Configuration
```bash
python test-runner.py --config custom-config.yaml
```

## 📊 Test Suites

### 1. Individual Agent Operations
**Duration:** ~10 minutes  
**Coverage:** All 37 agents  
**Tests:**
- Agent initialization and setup
- Core functionality validation
- Tool access verification
- Error handling capabilities
- Memory management testing

```bash
python test-runner.py --suites individual_operations
```

### 2. Inter-Agent Communication
**Duration:** ~15 minutes  
**Coverage:** All delegation and coordination relationships  
**Tests:**
- Agent handoff protocols
- Context data integrity
- Communication latency
- Delegation chain validation

```bash
python test-runner.py --suites inter_agent_communication
```

### 3. Context Preservation
**Duration:** ~20 minutes  
**Coverage:** Multi-agent workflows  
**Tests:**
- Context data preservation across handoffs
- Schema validation
- Data corruption detection
- Context size optimization

```bash
python test-runner.py --suites context_preservation
```

### 4. Error Scenarios
**Duration:** ~15 minutes  
**Coverage:** Failure conditions and recovery  
**Tests:**
- Agent timeout handling
- Crash and recovery testing
- Dependency failure scenarios
- Resource exhaustion handling
- Circular delegation detection

```bash
python test-runner.py --suites error_scenarios
```

### 5. Performance Benchmarks
**Duration:** ~25 minutes  
**Coverage:** Performance metrics and regression detection  
**Tests:**
- Execution time benchmarking
- Memory usage profiling
- Concurrent execution testing
- Scalability limit identification
- Baseline comparison

```bash
python test-runner.py --suites performance_benchmarks
```

### 6. Load Testing
**Duration:** ~40 minutes  
**Coverage:** System stress testing  
**Tests:**
- Light load (5 concurrent users)
- Medium load (15 concurrent users)
- Heavy load (30 concurrent users)
- Stress testing (50 concurrent users)

```bash
python test-runner.py --suites load_testing
```

### 7. Integration Testing
**Duration:** ~60 minutes  
**Coverage:** Complete workflow validation  
**Tests:**
- End-to-end project delivery
- BMAD business model creation
- Security implementation workflow
- Quality assurance pipeline

```bash
python test-runner.py --suites integration_testing
```

## 🔧 Configuration

### Test Configuration File
The main configuration is in `config/test-config.yaml`. Key sections:

```yaml
# Execution settings
execution:
  test_timeout: 300
  parallel_execution: true
  max_workers: 8

# Performance thresholds
performance_thresholds:
  single_agent:
    max_execution_time: 30.0
    max_memory_usage: 512  # MB
    min_success_rate: 0.95

# Quality gates
ci_cd:
  quality_gates:
    minimum_test_coverage: 0.80
    maximum_failure_rate: 0.05
    maximum_regression_count: 3
```

### Environment Variables
```bash
# Optional environment configuration
export AGENT_TEST_CONFIG="tests/config/test-config.yaml"
export AGENT_TEST_TIMEOUT="300"
export AGENT_TEST_PARALLEL="true"
export AGENT_TEST_VERBOSE="false"
```

## 📈 Reports and Results

### Report Formats
Tests generate multiple report formats:
- **HTML Reports:** `tests/reports/test-report-TIMESTAMP.html`
- **JSON Results:** `tests/reports/test-results-TIMESTAMP.json`
- **JUnit XML:** `tests/reports/junit-results-TIMESTAMP.xml`
- **CSV Data:** `tests/reports/test-results-TIMESTAMP.csv`

### Viewing Results
```bash
# Open HTML report in browser
open tests/reports/test-report-latest.html

# View JSON results
cat tests/reports/test-results-latest.json | jq '.summary'

# Check test logs
tail -f tests/logs/agent-test-execution.log
```

## 🔄 CI/CD Integration

### GitHub Actions
Generate GitHub Actions workflow:
```bash
python ci-cd-integration.py --action generate-github
```

This creates `.github/workflows/agent-tests.yml` with:
- Matrix testing across Python versions
- Parallel test execution
- Artifact collection
- Quality gate validation

### Jenkins Pipeline
Generate Jenkins pipeline:
```bash
python ci-cd-integration.py --action generate-jenkins
```

Creates `Jenkinsfile` with:
- Parallel stage execution
- Test result publishing
- HTML report generation
- Email notifications

### Pre-commit Hooks
Setup automated pre-commit testing:
```bash
python ci-cd-integration.py --action setup-hooks
pre-commit install
```

## 🎯 Quality Gates

### Automatic Validation
Quality gates are automatically validated after test execution:

```bash
python validate-quality-gates.py
```

### Quality Metrics
- **Test Coverage:** ≥80%
- **Success Rate:** ≥95%
- **Regression Count:** ≤3
- **Performance Score:** ≥75%
- **Critical Failures:** 0

### Pipeline Integration
```bash
# Validate and fail pipeline if gates don't pass
python validate-quality-gates.py --fail-on-violation
```

## 🧪 Advanced Testing

### Custom Test Data
Generate custom test scenarios:
```python
from agent_test_framework import AgentTestFramework

framework = AgentTestFramework()
# Add custom test data
framework.mock_environment.add_custom_scenario("my_scenario", config)
```

### Performance Baselines
Update performance baselines:
```bash
python test-runner.py --update-baselines
```

### Debug Mode
Enable detailed debugging:
```bash
python test-runner.py --debug --log-level DEBUG
```

## 📊 Agent Coverage

### Core Agents (27)
**Tier 0 Coordination (2):**
- master-orchestrator
- ceo-strategy

**Tier 1 Orchestration (3):**
- business-tech-alignment
- project-manager
- technical-cto

**Tier 2 Teams (19):**
- Analysis: business-analyst, financial-analyst
- Design: ui-ux-design, frontend-architecture, database-architecture, security-architecture
- Implementation: backend-services, frontend-mockup, production-frontend, mobile-development, integration-setup
- Operations: devops-engineering, performance-optimization, script-automation
- Quality: quality-assurance, testing-automation, technical-specifications

**Tier 3 Specialists (3):**
- api-integration-specialist
- middleware-specialist
- prompt-engineer

### BMAD Agents (10)
**Tier 1 BMAD (4):**
- bmad-business-model
- bmad-architecture-design
- bmad-design
- bmad-workflow-coordinator

**Tier 2 BMAD (6):**
- bmad-market-research
- bmad-technical-planning
- bmad-user-experience
- bmad-visual-design
- bmad-validation
- bmad-integration

## 🚨 Troubleshooting

### Common Issues

#### Agent Discovery Fails
```bash
# Check agent files exist
find core/agents tier1 tier2 -name "*.md" | wc -l
# Should show 37 files

# Verify agent metadata
python -c "from agent_test_framework import AgentTestFramework; f = AgentTestFramework(); print([a.name for a in f.agents])"
```

#### Tests Timeout
```bash
# Increase timeout in config
# Edit config/test-config.yaml:
# execution:
#   test_timeout: 600  # Increase from 300

# Or run with custom timeout
python test-runner.py --timeout 600
```

#### Memory Issues
```bash
# Reduce parallel workers
# Edit config/test-config.yaml:
# execution:
#   max_workers: 4  # Reduce from 8

# Or disable parallel execution
python test-runner.py --no-parallel
```

#### Permission Errors
```bash
# Ensure proper permissions
chmod +x test-runner.py
chmod -R 755 tests/

# Check log directory permissions
mkdir -p tests/logs
chmod 755 tests/logs
```

### Debug Commands
```bash
# Test framework initialization
python -c "from agent_test_framework import AgentTestFramework; AgentTestFramework()"

# Check configuration loading
python -c "import yaml; print(yaml.safe_load(open('config/test-config.yaml')))"

# Verify dependencies
pip check

# Test individual components
python -m pytest tests/unit/ -v
```

## 📝 Contributing

### Adding New Tests
1. Create test in appropriate framework file
2. Update configuration if needed
3. Add to test suite in `test-runner.py`
4. Update documentation

### Performance Baseline Updates
When adding new agents or modifying existing ones:
```bash
# Run baseline update
python test-runner.py --update-baselines --suites performance_benchmarks

# Commit new baselines
git add tests/baselines/
git commit -m "Update performance baselines for new agents"
```

### Test Data Management
```bash
# Generate new test data
python generate-test-data.py --agents all --scenarios comprehensive

# Clean old test data
python cleanup-test-data.py --older-than 30d
```

## 📊 Metrics and Monitoring

### Real-time Monitoring
```bash
# Monitor test execution
tail -f tests/logs/agent-test-execution.log | grep -E "(ERROR|WARN|FAIL)"

# Watch test progress
watch "python test-status.py"
```

### Performance Tracking
```bash
# Generate performance trends
python generate-performance-trends.py --days 30

# Compare with baselines
python compare-baselines.py --current tests/reports/latest.json
```

## 🔐 Security Considerations

### Test Data Security
- No production data used in tests
- All test data is synthetic or anonymized
- Secure cleanup of temporary files
- No secrets in test configurations

### Access Control
- Test execution requires appropriate permissions
- Results contain no sensitive information
- Secure storage of test artifacts

## 📞 Support

### Getting Help
1. Check this README and troubleshooting section
2. Review test logs in `tests/logs/`
3. Check GitHub issues for similar problems
4. Create new issue with detailed error information

### Contact Information
- **Framework Maintainer:** Claude Code Testing Team
- **Documentation:** `tests/README.md`
- **Configuration:** `tests/config/test-config.yaml`
- **Issues:** Create GitHub issue with logs and configuration

---

## 🎉 Success Criteria

Your test suite is working correctly when:
- ✅ All 37 agents are discovered and tested
- ✅ Individual agent tests pass with >95% success rate
- ✅ Inter-agent communication validates correctly
- ✅ Context preservation maintains >90% integrity
- ✅ Error scenarios handle failures gracefully
- ✅ Performance benchmarks meet baseline requirements
- ✅ Load testing completes without critical failures
- ✅ Integration workflows execute end-to-end successfully
- ✅ Quality gates pass validation
- ✅ Reports generate in all configured formats

**Happy Testing! 🚀**