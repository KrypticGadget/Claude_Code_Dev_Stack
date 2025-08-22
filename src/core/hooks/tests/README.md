# Hook Test Framework V3.6.9

A comprehensive testing framework for all 38 hooks in the Claude Code Agents system, providing extensive testing capabilities including individual hook functionality, hook chain testing, error scenarios, performance testing, integration testing, concurrency testing, and regression testing.

## 🎯 Overview

The Hook Test Framework provides a complete testing solution for the Claude Code Agents hook system with the following key features:

- **Individual Hook Testing**: Test each of 38 hooks in isolation
- **Hook Chain Testing**: Test sequences of dependent hooks
- **Error Scenario Testing**: Handle hook failures and recovery
- **Performance Testing**: Load testing and benchmark validation
- **Integration Testing**: LSP bridge and hook registry integration
- **Concurrency Testing**: Multiple hooks executing simultaneously
- **Regression Testing**: Prevent breaking changes

## 📁 Project Structure

```
tests/
├── test_framework.py          # Main test framework implementation
├── test_utilities.py          # Testing utilities and helpers
├── test_runner.py             # Test runner with CI/CD integration
├── conftest.py               # pytest configuration and fixtures
├── test_pytest_integration.py # pytest-based tests
├── pytest.ini               # pytest configuration
├── .coveragerc              # Coverage configuration
├── test_config.yaml         # Test framework configuration
├── ci/                      # CI/CD configuration files
│   ├── github_actions.yml   # GitHub Actions workflow
│   └── jenkins_pipeline.groovy # Jenkins pipeline
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- All hook dependencies installed
- pytest and related testing packages

### Installation

1. Install required packages:
```bash
cd core/hooks
pip install -r requirements.txt
pip install pytest pytest-cov pytest-xdist pytest-timeout pytest-html
```

2. Verify installation:
```bash
cd tests
python -c "import test_framework; print('Framework loaded successfully')"
```

### Running Tests

#### Basic Usage

```bash
# Run all tests
python test_runner.py

# Run specific test suite
python test_runner.py --suite individual_functionality

# Run specific hook test
python test_runner.py --hook smart_orchestrator

# Interactive mode
python test_runner.py --mode interactive
```

#### Using pytest

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m performance
pytest -m concurrency
pytest -m regression
pytest -m smoke

# Run with coverage
pytest --cov=../ --cov-report=html

# Run in parallel
pytest -n auto
```

#### CI/CD Mode

```bash
# Run in CI/CD mode
python test_runner.py --mode ci

# Run with specific filter
python test_runner.py --mode ci --filter smoke

# Update performance baselines
python test_runner.py --mode ci --update-baselines
```

## 🧪 Test Suites

### 1. Individual Hook Functionality
Tests each of the 38 hooks in isolation:

```python
# Example: Test individual hook
framework = HookTestFramework()
result = framework.test_individual_hook("smart_orchestrator")
print(f"Result: {result.status}")
```

**Covered Hooks:**
- **Orchestration**: smart_orchestrator, master_orchestrator, v3_orchestrator, orchestration_enhancer
- **Routing**: slash_command_router, agent_mention_parser, agent_enhancer_v3
- **Feedback**: audio_player_v3, audio_controller, audio_notifier, audio_player, audio_player_fixed
- **UI**: status_line_manager, chat_manager_v3, chat_manager, notification_sender
- **Automation**: auto_documentation, auto_formatter
- **Quality**: code_linter, quality_gate_hook, git_quality_hooks, security_scanner, dependency_checker
- **Monitoring**: performance_monitor, resource_monitor, model_tracker
- **State**: context_manager, session_loader, session_saver
- **Config**: v3_config, v3_validator
- **Workflow**: planning_trigger, parallel_execution_engine
- **Execution**: enhanced_bash_hook, venv_enforcer
- **Special**: ultimate_claude_hook
- **Migration**: migrate_to_v3_audio

### 2. Hook Chain Testing
Tests sequences of dependent hooks:

```python
# Example: Test orchestration chain
result = framework.test_orchestration_chain()
```

**Chain Types:**
- **Orchestration Chain**: smart_orchestrator → master_orchestrator → v3_orchestrator
- **Quality Gate Chain**: code_linter → security_scanner → quality_gate_hook
- **Session Management Chain**: session_loader → context_manager → session_saver
- **Audio Feedback Chain**: audio_player_v3 → audio_controller → notification_sender

### 3. Error Scenario Testing
Tests hook behavior under various error conditions:

```python
# Example: Test timeout handling
result = framework.test_hook_timeout_handling()
```

**Error Scenarios:**
- Hook timeout handling
- Dependency failure recovery
- Resource exhaustion handling
- Invalid input handling
- File system errors

### 4. Performance Testing
Tests hook performance and benchmarks:

```python
# Example: Performance benchmarking
result = framework.test_hook_execution_benchmarks()
```

**Performance Tests:**
- Hook execution benchmarks
- Concurrent execution performance
- Memory usage patterns
- Resource cleanup efficiency

### 5. Integration Testing
Tests integration with external systems:

```python
# Example: LSP integration
result = framework.test_lsp_bridge_integration()
```

**Integration Tests:**
- LSP bridge integration
- Hook registry synchronization
- API integration
- Configuration integration

### 6. Concurrency Testing
Tests concurrent hook execution:

```python
# Example: Parallel execution
result = framework.test_parallel_hook_execution()
```

**Concurrency Tests:**
- Parallel hook execution
- Resource contention handling
- Deadlock detection
- Thread safety

### 7. Regression Testing
Tests for breaking changes:

```python
# Example: Backward compatibility
result = framework.test_backward_compatibility()
```

**Regression Tests:**
- Backward compatibility
- API contract compliance
- Configuration migration
- Performance regression

## 🔧 Configuration

### Test Configuration File
The framework uses `test_config.yaml` for comprehensive configuration:

```yaml
# Global settings
global:
  timeout_seconds: 1800
  parallel_execution: true
  max_workers: 8

# Performance settings
performance:
  regression_threshold: 1.5
  memory_threshold_mb: 100
  
# Quality gates
quality_gates:
  required_pass_rate: 85.0
  coverage_threshold: 75.0
```

### Environment Variables
```bash
export PYTEST_RUNNING=1
export TEST_ENVIRONMENT=framework
export PYTHONPATH=../
```

## 📊 Reporting

### HTML Reports
Comprehensive HTML reports with:
- Test execution summary
- Performance metrics
- Coverage information
- Error details
- Interactive charts

### JUnit XML
CI/CD compatible XML reports for:
- Test results
- Execution times
- Failure details

### Performance Reports
Detailed performance analysis:
- Execution time trends
- Memory usage patterns
- Performance regression detection
- Benchmark comparisons

### Coverage Reports
Code coverage analysis:
- Line coverage
- Branch coverage
- Function coverage
- Missing code identification

## 🔄 CI/CD Integration

### GitHub Actions
Automated testing on:
- Push to main/develop branches
- Pull requests
- Scheduled runs (daily)

```yaml
# .github/workflows/hook-tests.yml
name: Hook Test Framework CI/CD
on: [push, pull_request, schedule]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: python test_runner.py --mode ci
```

### Jenkins Pipeline
Enterprise CI/CD with:
- Multi-branch support
- Parallel execution
- Quality gates
- Notifications

```groovy
// Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'python test_runner.py --mode ci'
            }
        }
    }
}
```

## 🛠️ Development

### Adding New Tests

1. **Individual Hook Test**:
```python
def test_my_new_hook(self, mock_hook_manager):
    result = mock_hook_manager.execute_hook("my_new_hook", "test", {})
    assert result is not None
```

2. **Hook Chain Test**:
```python
def test_my_hook_chain(self, mock_hook_manager):
    chain_hooks = ["hook1", "hook2", "hook3"]
    for hook in chain_hooks:
        mock_hook_manager.activate_hook(hook)
    # Test chain execution
```

3. **Performance Test**:
```python
@pytest.mark.performance
def test_my_hook_performance(self, performance_monitor):
    # Test with performance monitoring
    pass
```

### Custom Test Data
```python
from test_utilities import TestDataGenerator

generator = TestDataGenerator()
user_data = generator.generate_user_prompt_data()
claude_data = generator.generate_claude_response_data()
```

### Mock Environments
```python
from test_utilities import TestEnvironmentManager

with TestEnvironmentManager("my_test") as env:
    test_file = env.create_test_file("test.py", "content")
    config = env.create_test_config({"key": "value"})
```

## 📈 Performance Monitoring

### Baseline Management
```bash
# Update performance baselines
python test_runner.py --update-baselines

# Compare against baselines
python test_runner.py --mode ci --filter performance
```

### Memory Profiling
```python
from test_utilities import PerformanceProfiler

with PerformanceProfiler("my_hook") as profiler:
    # Execute hook
    pass

metrics = profiler.get_metrics()
```

### Concurrency Testing
```python
from test_utilities import ConcurrencyTester

tester = ConcurrencyTester(max_workers=5)
results = tester.execute_concurrent_hooks(hook_executor, test_data)
analysis = tester.analyze_concurrency_results(results)
```

## 🐛 Debugging

### Debug Mode
```bash
# Enable debug mode
python test_runner.py --debug

# Verbose logging
pytest -v -s

# Preserve temp files
export DEBUG_PRESERVE_TEMP=1
```

### Test Isolation
```python
# Use isolated environment
from test_utilities import isolated_test_environment

with isolated_test_environment("debug_test") as env:
    # Debug-specific testing
    pass
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure PYTHONPATH includes hook directory
   - Check all dependencies are installed

2. **Timeout Issues**:
   - Increase timeout in pytest.ini
   - Use `@pytest.mark.timeout(seconds)` for specific tests

3. **Mock Failures**:
   - Verify mock setup in conftest.py
   - Check mock return values

4. **Performance Issues**:
   - Update baselines if legitimate improvements
   - Check for resource leaks

### Getting Help

1. Check test logs: `pytest --log-cli-level=DEBUG`
2. Run in interactive mode: `python test_runner.py --mode interactive`
3. Generate detailed reports: `pytest --html=detailed_report.html`

## 📝 Best Practices

### Test Writing
- Use descriptive test names
- Keep tests focused and atomic
- Use appropriate pytest markers
- Include performance considerations
- Handle cleanup properly

### Performance Testing
- Always compare against baselines
- Monitor memory usage
- Test under various loads
- Consider concurrency implications

### Error Handling
- Test both success and failure cases
- Verify graceful degradation
- Check resource cleanup
- Validate error messages

## 🤝 Contributing

1. **Add Tests**: Cover new hooks or scenarios
2. **Improve Framework**: Enhance testing capabilities
3. **Documentation**: Update this README
4. **Performance**: Optimize test execution
5. **CI/CD**: Improve automation

### Pull Request Process
1. Add tests for new functionality
2. Ensure all tests pass
3. Update documentation
4. Include performance impact analysis

## 📜 License

This test framework is part of the Claude Code Agents project. See the main project LICENSE file for details.

## 🙏 Acknowledgments

- Claude Code Agents development team
- pytest and testing community
- CI/CD tooling providers
- Performance monitoring libraries

---

**For more information, see the individual test files and configuration documentation.**