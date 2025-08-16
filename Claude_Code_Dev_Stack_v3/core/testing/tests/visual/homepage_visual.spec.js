// Visual Regression Test Example for Homepage
// Demonstrates headed browser testing with screenshot comparison

const { test, expect } = require('@playwright/test');

test.describe('Homepage Visual Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to homepage before each test
    await page.goto('/');
    
    // Wait for page to fully load
    await page.waitForLoadState('networkidle');
    
    // Wait for any animations to complete
    await page.waitForTimeout(1000);
  });

  test('homepage full page visual regression', async ({ page }) => {
    // Hide dynamic elements that change frequently
    await page.addStyleTag({
      content: `
        .timestamp, .live-clock, .random-id { 
          visibility: hidden !important; 
        }
      `
    });

    // Take full page screenshot and compare with baseline
    await expect(page).toHaveScreenshot('homepage-full.png', {
      fullPage: true,
      threshold: 0.3, // Allow 30% difference for dynamic content
      maxDiffPixels: 1000
    });
  });

  test('header section visual regression', async ({ page }) => {
    // Test specific section
    const header = page.locator('header');
    
    await expect(header).toHaveScreenshot('homepage-header.png', {
      threshold: 0.2
    });
  });

  test('navigation menu visual regression', async ({ page }) => {
    // Test navigation in different states
    const nav = page.locator('nav');
    
    // Default state
    await expect(nav).toHaveScreenshot('nav-default.png');
    
    // Hover state (if applicable)
    await nav.locator('a').first().hover();
    await expect(nav).toHaveScreenshot('nav-hover.png');
  });

  test('responsive design visual tests', async ({ page }) => {
    // Test different viewport sizes
    const viewports = [
      { width: 1920, height: 1080, name: 'desktop' },
      { width: 1024, height: 768, name: 'tablet' },
      { width: 375, height: 667, name: 'mobile' }
    ];

    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.waitForTimeout(500); // Allow layout to adjust
      
      await expect(page).toHaveScreenshot(`homepage-${viewport.name}.png`, {
        fullPage: true,
        threshold: 0.3
      });
    }
  });

  test('dark mode visual regression', async ({ page }) => {
    // Test dark mode if available
    const darkModeToggle = page.locator('[data-testid="dark-mode-toggle"]');
    
    if (await darkModeToggle.isVisible()) {
      await darkModeToggle.click();
      await page.waitForTimeout(500); // Wait for theme transition
      
      await expect(page).toHaveScreenshot('homepage-dark-mode.png', {
        fullPage: true,
        threshold: 0.3
      });
    }
  });

  test('accessibility visual indicators', async ({ page }) => {
    // Test focus indicators and accessibility features
    await page.keyboard.press('Tab'); // Focus first element
    await expect(page).toHaveScreenshot('homepage-focus-first.png');
    
    // Continue tabbing through interactive elements
    for (let i = 0; i < 3; i++) {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(200);
    }
    
    await expect(page).toHaveScreenshot('homepage-focus-navigation.png');
  });

  test('loading states visual test', async ({ page }) => {
    // Test loading states by throttling network
    await page.route('**/*', route => {
      setTimeout(() => route.continue(), 1000); // Add 1s delay
    });
    
    // Navigate and capture loading state
    const navigationPromise = page.goto('/', { waitUntil: 'domcontentloaded' });
    
    // Capture loading state
    await page.waitForSelector('.loading-spinner', { timeout: 5000 }).catch(() => {});
    await expect(page).toHaveScreenshot('homepage-loading.png');
    
    await navigationPromise;
  });

  test('form visual states', async ({ page }) => {
    // Test form appearance and validation states
    const contactForm = page.locator('[data-testid="contact-form"]');
    
    if (await contactForm.isVisible()) {
      // Empty form state
      await expect(contactForm).toHaveScreenshot('form-empty.png');
      
      // Filled form state
      await page.fill('[data-testid="name-input"]', 'John Doe');
      await page.fill('[data-testid="email-input"]', 'john@example.com');
      await page.fill('[data-testid="message-input"]', 'Test message content');
      
      await expect(contactForm).toHaveScreenshot('form-filled.png');
      
      // Validation error state
      await page.fill('[data-testid="email-input"]', 'invalid-email');
      await page.blur('[data-testid="email-input"]');
      await page.waitForTimeout(500); // Wait for validation
      
      await expect(contactForm).toHaveScreenshot('form-validation-error.png');
    }
  });

  test('interactive elements hover states', async ({ page }) => {
    // Test button hover states
    const buttons = page.locator('button, .btn, [role="button"]');
    const buttonCount = await buttons.count();
    
    if (buttonCount > 0) {
      for (let i = 0; i < Math.min(buttonCount, 3); i++) {
        const button = buttons.nth(i);
        await button.hover();
        await expect(button).toHaveScreenshot(`button-hover-${i}.png`);
      }
    }
  });

  test('animated elements visual test', async ({ page }) => {
    // Disable animations for consistent screenshots
    await page.addStyleTag({
      content: `
        *, *::before, *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
        }
      `
    });
    
    await expect(page).toHaveScreenshot('homepage-no-animations.png', {
      fullPage: true
    });
  });
});