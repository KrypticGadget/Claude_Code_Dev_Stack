# Claude Code Dev Stack v3.0 - Integration Testing Suite

This comprehensive integration testing suite validates all major components and their interactions within the Claude Code Dev Stack v3.0.

## Overview

The integration testing suite covers:

- **Python Components**: MCP generator, semantic analysis, LSP hooks
- **TypeScript/Node.js Components**: OpenAPI generator, LSP daemon, semantic API
- **React Web Application**: Frontend with PWA capabilities
- **Backend Services**: API servers and microservices
- **Cross-Component Integration**: End-to-end workflows and data flow validation
- **Performance Testing**: Load testing, memory usage, and scalability validation
- **Security Testing**: Vulnerability scanning and security validation

## Directory Structure

```
tests/integration/
├── README.md                 # This file
├── jest.config.js           # Jest configuration for TypeScript tests
├── pytest.ini              # Pytest configuration for Python tests
├── package.json             # Node.js dependencies and scripts
├── setup/
│   └── jest.setup.ts        # Jest test setup and utilities
├── python/
│   ├── conftest.py          # Pytest fixtures and configuration
│   ├── test_mcp_generator.py        # MCP generator tests
│   ├── test_semantic_analysis.py   # Semantic analysis tests
│   └── test_lsp_hooks.py           # LSP hooks tests
├── typescript/
│   ├── test_openapi_generator.test.ts  # OpenAPI generator tests
│   ├── test_lsp_daemon.test.ts        # LSP daemon tests
│   ├── test_semantic_api.test.ts      # Semantic API tests
│   └── test_web_frontend.test.ts      # Web frontend tests
├── e2e/
│   ├── test_full_pipeline.test.ts     # End-to-end pipeline tests
│   ├── test_user_workflows.test.ts    # User workflow tests
│   └── test_multi_service.test.ts     # Multi-service integration
├── benchmarks/
│   ├── performance_suite.py           # Performance benchmark suite
│   ├── load_testing.js               # Load testing scripts
│   └── memory_profiling.py           # Memory usage profiling
├── coverage/
│   ├── generate_report.py            # Coverage report generator
│   └── coverage-report.html          # Generated coverage report
└── data/
    ├── test_openapi_specs/           # Test OpenAPI specifications
    ├── sample_code/                  # Sample code for analysis
    └── fixtures/                     # Test data fixtures
```

## Test Categories

### 1. Unit Integration Tests

**Python Components:**
- **MCP Generator** (`test_mcp_generator.py`)
  - OpenAPI specification parsing
  - Code generation pipeline
  - Template rendering
  - File system operations
  - Error handling and validation

- **Semantic Analysis** (`test_semantic_analysis.py`)
  - Code complexity analysis
  - Pattern detection
  - Security vulnerability scanning
  - Multi-language support
  - Performance optimization

- **LSP Hooks** (`test_lsp_hooks.py`)
  - Audio hook integration
  - Quality orchestrator functionality
  - Event handling and notifications
  - Configuration management

**TypeScript Components:**
- **OpenAPI Generator** (`test_openapi_generator.test.ts`)
  - Tool extraction from OpenAPI specs
  - Schema validation
  - API client generation
  - Error handling and recovery

- **LSP Daemon** (`test_lsp_daemon.test.ts`)
  - Language server protocol implementation
  - Document synchronization
  - Hook integration
  - Performance under load

- **Semantic API** (`test_semantic_api.test.ts`)
  - REST API endpoints
  - Real-time analysis
  - Caching mechanisms
  - Concurrent request handling

### 2. End-to-End Integration Tests

**Full Pipeline Tests** (`test_full_pipeline.test.ts`)
- Complete workflow from OpenAPI spec to working MCP tools
- Multi-service coordination
- Data flow validation
- Error propagation and recovery

**User Workflow Tests** (`test_user_workflows.test.ts`)
- Developer experience scenarios
- IDE integration workflows
- Code analysis and improvement cycles
- Collaborative development features

### 3. Performance Tests

**Performance Benchmark Suite** (`performance_suite.py`)
- Component-level performance metrics
- Memory usage profiling
- CPU utilization monitoring
- Throughput measurements

**Load Testing** (`load_testing.js`)
- High-concurrency scenarios
- API endpoint stress testing
- Database performance under load
- Memory leak detection

### 4. Security Tests

**Security Validation**
- Input validation testing
- Authentication and authorization
- Data sanitization
- Vulnerability scanning
- Secure communication protocols

## Running Tests

### Prerequisites

1. **Node.js** (v18 or higher)
2. **Python** (3.11 or higher)
3. **Required Dependencies**:
   ```bash
   # Install Node.js dependencies
   npm install
   
   # Install Python dependencies
   pip install pytest pytest-cov pytest-xdist pytest-mock aiohttp httpx
   ```

### Running All Tests

```bash
# Run complete integration test suite
npm run test:all

# Run with coverage
npm run test:coverage
```

### Running Specific Test Categories

**Python Tests:**
```bash
# Run all Python integration tests
npm run test:python

# Run specific test file
pytest python/test_mcp_generator.py -v

# Run with coverage
pytest python/ --cov=../../core --cov-report=html
```

**TypeScript Tests:**
```bash
# Run all TypeScript integration tests
npm run test:typescript

# Run specific test file
npm test typescript/test_openapi_generator.test.ts

# Run with coverage
npm run test:coverage
```

**End-to-End Tests:**
```bash
# Run E2E tests
npm run test:e2e

# Run specific E2E scenario
npm test e2e/test_full_pipeline.test.ts
```

**Performance Tests:**
```bash
# Run performance benchmarks
npm run test:performance

# Run Python performance tests
pytest benchmarks/performance_suite.py -m performance

# Run load testing
node benchmarks/load_testing.js
```

### Running Tests by Marker

**Python Test Markers:**
```bash
# Run only MCP generator tests
pytest -m mcp

# Run only semantic analysis tests
pytest -m semantic

# Run only performance tests
pytest -m performance

# Run only integration tests (exclude unit tests)
pytest -m integration
```

**Jest Test Patterns:**
```bash
# Run tests matching pattern
npm test -- --testNamePattern="performance"

# Run tests in specific directory
npm test typescript/

# Run tests with specific timeout
npm test -- --testTimeout=60000
```

## Continuous Integration

### GitHub Actions Workflow

The integration tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests
- Scheduled daily runs (2 AM UTC)

**Workflow Stages:**
1. **Setup**: Environment preparation and dependency installation
2. **Python Tests**: Run pytest with coverage reporting
3. **TypeScript Tests**: Run Jest with coverage reporting
4. **E2E Tests**: Full pipeline validation
5. **Performance Tests**: Benchmark execution (scheduled only)
6. **Security Tests**: Vulnerability scanning
7. **Coverage Reporting**: Generate and publish coverage reports

### Coverage Requirements

- **Minimum Line Coverage**: 80%
- **Minimum Branch Coverage**: 70%
- **Minimum Function Coverage**: 80%

Components below these thresholds will cause CI failure.

## Test Data and Fixtures

### OpenAPI Specifications

Located in `data/test_openapi_specs/`:
- `petstore.yaml` - Simple API for basic testing
- `complex_api.yaml` - Complex API with nested schemas
- `large_api.yaml` - Large API for performance testing
- `invalid_specs/` - Invalid specs for error handling tests

### Sample Code

Located in `data/sample_code/`:
- Python files with various complexity levels
- TypeScript files with different patterns
- Code with intentional issues for detection testing

### Test Fixtures

Located in `data/fixtures/`:
- Database fixtures
- Mock API responses
- Configuration files
- Test user data

## Configuration

### Jest Configuration (`jest.config.js`)

```javascript
{
  preset: 'ts-jest',
  testEnvironment: 'node',
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/setup/jest.setup.ts']
}
```

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = python/
addopts = 
    --cov=../../core
    --cov-report=html
    --cov-fail-under=80
    --verbose
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow running tests
```

## Coverage Reporting

### Generating Coverage Reports

```bash
# Generate comprehensive coverage report
python coverage/generate_report.py

# View HTML coverage report
open coverage/coverage-report.html
```

### Coverage Report Formats

- **HTML**: Interactive coverage report with line-by-line analysis
- **JSON**: Machine-readable coverage data
- **XML**: JUnit-compatible format for CI integration
- **Markdown**: Human-readable summary for documentation

## Performance Benchmarking

### Running Benchmarks

```bash
# Run all performance benchmarks
python benchmarks/performance_suite.py

# Run specific benchmark category
pytest benchmarks/ -m "performance and mcp"

# Generate performance report
python benchmarks/performance_suite.py --report
```

### Performance Metrics

Tracked metrics include:
- **Execution Time**: Function and method execution times
- **Memory Usage**: Peak and average memory consumption
- **CPU Utilization**: Processor usage during operations
- **Throughput**: Operations per second
- **Latency**: Response times for API calls

### Performance Thresholds

- MCP generation: < 5 seconds for 100 endpoints
- Semantic analysis: < 2 seconds for 1000 lines of code
- LSP responses: < 100ms for hover/completion requests
- API throughput: > 100 requests/second

## Debugging Tests

### Running Tests in Debug Mode

**Python:**
```bash
# Run with verbose output
pytest -v -s python/test_mcp_generator.py

# Run with debugging
pytest --pdb python/test_mcp_generator.py

# Run specific test method
pytest python/test_mcp_generator.py::TestMCPGenerator::test_spec_loading_yaml
```

**TypeScript:**
```bash
# Run with verbose output
npm test -- --verbose

# Run in watch mode
npm test -- --watch

# Debug specific test
npm test -- --testNamePattern="should extract tools"
```

### Common Issues and Solutions

1. **Import Errors**:
   - Ensure PYTHONPATH includes project root
   - Verify all dependencies are installed

2. **Timeout Issues**:
   - Increase test timeout for slow operations
   - Use `pytest.mark.slow` for long-running tests

3. **Mock Issues**:
   - Ensure mocks are properly reset between tests
   - Use `pytest.fixture(autouse=True)` for automatic cleanup

4. **Coverage Issues**:
   - Check that all source files are included in coverage
   - Exclude test files and generated code from coverage

## Contributing

### Adding New Tests

1. **Create Test File**:
   - Python: `test_new_component.py`
   - TypeScript: `test_new_component.test.ts`

2. **Add Appropriate Markers**:
   ```python
   @pytest.mark.integration
   @pytest.mark.component_name
   def test_new_functionality():
       pass
   ```

3. **Update CI Configuration**:
   - Add new test paths to workflow
   - Update coverage requirements if needed

4. **Document Test Purpose**:
   - Add docstrings explaining test objectives
   - Update this README with new test categories

### Test Best Practices

- **Isolation**: Each test should be independent
- **Clarity**: Test names should clearly describe what's being tested
- **Coverage**: Aim for comprehensive coverage of happy path and edge cases
- **Performance**: Keep tests fast; use `@pytest.mark.slow` for exceptions
- **Reliability**: Tests should be deterministic and not flaky

## Maintenance

### Regular Tasks

- **Weekly**: Review test performance and optimize slow tests
- **Monthly**: Update test data and fixtures
- **Quarterly**: Review coverage requirements and adjust thresholds
- **As Needed**: Update tests when adding new features

### Monitoring

- CI test execution times
- Test flakiness rates
- Coverage trends over time
- Performance benchmark trends

For questions or issues with the integration test suite, please check the GitHub Issues or contact the development team.