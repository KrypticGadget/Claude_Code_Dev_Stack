# Playwright Headed Browser Automation & Visual Testing

This comprehensive testing framework provides headed browser automation with visual regression testing, form automation, accessibility testing, and cross-browser compatibility validation.

## Features

- **Headed Browser Testing**: Visual browser automation with Chrome, Firefox, and Safari
- **Visual Regression Testing**: Advanced screenshot comparison with pixel-level accuracy
- **Form Automation**: Comprehensive form filling and validation testing
- **Accessibility Testing**: WCAG compliance validation using axe-core
- **Cross-Browser Testing**: Automated testing across multiple browsers
- **Video Recording**: Capture test execution videos for debugging
- **Network Monitoring**: HAR file generation for network analysis
- **Real-time Reporting**: HTML reports with visual diff comparison

## Quick Start

### Windows Batch Scripts

Run headed browser tests with pre-configured batch scripts:

```bash
# Chrome (Chromium)
launch_headed_chrome.bat

# Firefox
launch_headed_firefox.bat

# Safari (WebKit)
launch_headed_safari.bat
```

### Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install
   playwright install-deps
   ```

2. **JavaScript Setup**
   ```bash
   npm install
   npm run install:browsers
   ```

3. **Run Tests**
   ```bash
   # Python Visual Testing Framework
   python launch_headed_testing.py --browser chromium --test-suite all

   # JavaScript Playwright Tests
   npm run test:headed
   ```

## Configuration Options

### Python Framework Options

```bash
python launch_headed_testing.py [OPTIONS]

Options:
  --browser {chromium,firefox,webkit}  Browser to use (default: chromium)
  --headless                          Run in headless mode (default: headed)
  --viewport-width INTEGER            Browser width (default: 1920)
  --viewport-height INTEGER           Browser height (default: 1080)
  --slow-mo INTEGER                   Slow motion delay in ms (default: 500)
  --record-video                      Record test execution video
  --record-har                        Record network activity
  --output-dir TEXT                   Output directory (default: test_outputs)
  --test-suite {visual,form,accessibility,cross-browser,all}
  --base-url TEXT                     Base URL for testing (default: http://localhost:3000)
  --config-file TEXT                  Path to JSON configuration file
```

### JavaScript Test Commands

```bash
# Run specific test suites
npm run test:visual          # Visual regression tests
npm run test:form           # Form automation tests
npm run test:accessibility  # Accessibility tests

# Run on specific browsers
npm run test:chrome         # Chrome headed mode
npm run test:firefox        # Firefox headed mode
npm run test:safari         # Safari headed mode

# Cross-browser testing
npm run test:cross-browser  # All browsers in parallel

# Development tools
npm run test:debug          # Debug mode with pause on failure
npm run test:ui             # Interactive UI mode
npm run codegen             # Generate test code
```

## Test Structure

```
core/testing/
├── playwright_visual_testing.py    # Python visual testing framework
├── playwright.config.js            # Playwright configuration
├── launch_headed_testing.py        # Python test launcher
├── requirements.txt                 # Python dependencies
├── package.json                    # Node.js dependencies
├── tests/
│   ├── visual/
│   │   └── homepage_visual.spec.js # Visual regression tests
│   ├── form-automation/
│   │   └── contact_form.spec.js    # Form automation tests
│   ├── accessibility/
│   │   └── a11y.spec.js           # Accessibility tests
│   └── cross-browser/
│       └── compatibility.spec.js   # Cross-browser tests
├── test_outputs/                   # Test artifacts
│   ├── screenshots/               # Current screenshots
│   ├── baselines/                 # Baseline images
│   ├── diffs/                     # Visual differences
│   ├── videos/                    # Test recordings
│   ├── har-files/                 # Network recordings
│   └── reports/                   # HTML reports
└── launch scripts/
    ├── launch_headed_chrome.bat   # Chrome launcher
    ├── launch_headed_firefox.bat  # Firefox launcher
    └── launch_headed_safari.bat   # Safari launcher
```

## Visual Testing Features

### Screenshot Comparison
- Pixel-perfect baseline comparison
- Configurable similarity thresholds
- Visual diff generation
- Responsive design validation

### Dynamic Element Masking
```javascript
// Mask changing elements before screenshot
await page.addStyleTag({
  content: '.timestamp, .live-clock { visibility: hidden !important; }'
});
```

### Responsive Testing
```javascript
const viewports = [
  { width: 1920, height: 1080, name: 'desktop' },
  { width: 1024, height: 768, name: 'tablet' },
  { width: 375, height: 667, name: 'mobile' }
];
```

## Form Automation Features

### Comprehensive Form Testing
- Text inputs, dropdowns, checkboxes, radio buttons
- File uploads and multi-step forms
- Form validation testing
- Auto-save functionality testing

### Example Form Configuration
```python
form_data = {
    "email": {
        "selector": "#email",
        "value": "test@example.com",
        "type": "email"
    },
    "password": {
        "selector": "#password",
        "value": "secure_password",
        "type": "password"
    },
    "remember": {
        "selector": "#remember-me",
        "value": True,
        "type": "checkbox"
    }
}
```

## Accessibility Testing

### WCAG Compliance
- Automated accessibility scanning with axe-core
- Keyboard navigation testing
- Focus indicator validation
- Color contrast checking

### Example Accessibility Test
```javascript
test('homepage accessibility', async ({ page }) => {
  await page.goto('/');
  
  const results = await page.evaluate(() => {
    return new Promise((resolve) => {
      axe.run().then((results) => {
        resolve(results);
      });
    });
  });
  
  expect(results.violations).toHaveLength(0);
});
```

## Cross-Browser Testing

### Supported Browsers
- **Chromium**: Chrome, Edge, Opera
- **Firefox**: Firefox and Firefox ESR
- **WebKit**: Safari on macOS/iOS

### Browser-Specific Configurations
```javascript
// Playwright configuration for each browser
projects: [
  {
    name: 'chromium-headed',
    use: { 
      ...devices['Desktop Chrome'],
      headless: false,
      launchOptions: { slowMo: 500, devtools: true }
    }
  },
  {
    name: 'firefox-headed',
    use: { 
      ...devices['Desktop Firefox'],
      headless: false,
      launchOptions: { slowMo: 500 }
    }
  }
]
```

## MCP Service Integration

The framework integrates with the MCP (Model Context Protocol) service for enhanced browser automation:

### API Endpoints
- `POST /page/{page_id}/visual-test` - Visual regression testing
- `POST /page/{page_id}/form-automation` - Form automation
- `POST /page/{page_id}/accessibility-test` - Accessibility testing
- `POST /cross-browser-test` - Cross-browser testing

### Example API Usage
```python
# Visual regression test via API
response = await client.post(
    f"http://localhost:8080/page/{page_id}/visual-test",
    json={
        "test_name": "homepage_header",
        "selector": "header",
        "full_page": False,
        "mask_selectors": [".timestamp", ".random-id"]
    }
)
```

## Debugging and Development

### Interactive Mode
```bash
# Open Playwright in interactive UI mode
npm run test:ui

# Generate test code interactively
npm run codegen
```

### Debug Mode
```bash
# Python debugging
python launch_headed_testing.py --browser chromium --slow-mo 2000

# JavaScript debugging
npm run test:debug
```

### Video Recording
All test executions can be recorded for later analysis:
```bash
python launch_headed_testing.py --record-video --browser chromium
```

## Reporting

### HTML Reports
- Visual test results with screenshot comparisons
- Form automation success/failure reports
- Accessibility violation summaries
- Cross-browser compatibility matrices

### Report Locations
- Python reports: `test_outputs/reports/`
- Playwright reports: `test-results/html-report/`

## Environment Variables

```bash
# Browser configuration
BROWSER_TYPE=chromium          # chromium, firefox, webkit
HEADLESS=false                 # true for headless mode
SLOW_MO=500                    # Milliseconds delay between actions
RECORD_VIDEO=false             # Enable video recording
RECORD_HAR=false               # Enable network recording

# Test configuration
BASE_URL=http://localhost:3000 # Application URL
OUTPUT_DIR=test_outputs        # Output directory
MCP_PORT=8080                  # MCP service port
```

## Best Practices

### Visual Testing
1. Use consistent viewport sizes
2. Mask dynamic content (timestamps, IDs)
3. Wait for animations to complete
4. Set appropriate similarity thresholds

### Form Testing
1. Test both valid and invalid inputs
2. Verify error message display
3. Test keyboard navigation
4. Validate form state persistence

### Accessibility Testing
1. Test with keyboard navigation only
2. Verify screen reader compatibility
3. Check color contrast ratios
4. Validate ARIA attributes

### Cross-Browser Testing
1. Test core functionality on all browsers
2. Verify responsive design consistency
3. Check browser-specific features
4. Validate JavaScript compatibility

## Troubleshooting

### Common Issues

**Browser Installation**
```bash
# Reinstall browsers
playwright install --force
playwright install-deps
```

**Permission Issues**
```bash
# Windows: Run as administrator
# Linux: Install system dependencies
sudo playwright install-deps
```

**Network Issues**
```bash
# Configure proxy if needed
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### Performance Optimization
- Use `--workers` flag for parallel execution
- Implement test data cleanup
- Use `--headed` only for debugging
- Configure appropriate timeouts

## Contributing

1. Add new test cases in appropriate directories
2. Update configuration files as needed
3. Document new features and APIs
4. Ensure cross-browser compatibility
5. Add visual baselines for new tests

## License

MIT License - see LICENSE file for details.