// Advanced Form Automation Test
// Demonstrates comprehensive form testing with headed browser

const { test, expect } = require('@playwright/test');

test.describe('Contact Form Automation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/contact');
    await page.waitForLoadState('networkidle');
  });

  test('complete form submission flow', async ({ page }) => {
    // Test data
    const formData = {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john.doe@example.com',
      phone: '+1-555-123-4567',
      company: 'Test Company Inc.',
      subject: 'Technical Support',
      message: 'This is a test message for automated form submission testing.',
      newsletter: true,
      terms: true
    };

    // Fill text inputs
    await page.fill('[data-testid="first-name"]', formData.firstName);
    await page.fill('[data-testid="last-name"]', formData.lastName);
    await page.fill('[data-testid="email"]', formData.email);
    await page.fill('[data-testid="phone"]', formData.phone);
    await page.fill('[data-testid="company"]', formData.company);

    // Select dropdown option
    await page.selectOption('[data-testid="subject"]', formData.subject);

    // Fill textarea
    await page.fill('[data-testid="message"]', formData.message);

    // Handle checkboxes
    if (formData.newsletter) {
      await page.check('[data-testid="newsletter"]');
    }
    
    await page.check('[data-testid="terms"]');

    // Verify form is filled correctly
    await expect(page.locator('[data-testid="first-name"]')).toHaveValue(formData.firstName);
    await expect(page.locator('[data-testid="email"]')).toHaveValue(formData.email);
    await expect(page.locator('[data-testid="newsletter"]')).toBeChecked();
    await expect(page.locator('[data-testid="terms"]')).toBeChecked();

    // Take screenshot before submission
    await expect(page).toHaveScreenshot('form-filled-before-submit.png');

    // Submit form
    await page.click('[data-testid="submit-button"]');

    // Wait for submission response
    await page.waitForSelector('[data-testid="success-message"]', { timeout: 10000 });

    // Verify success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Thank you');

    // Take screenshot after successful submission
    await expect(page).toHaveScreenshot('form-success-message.png');
  });

  test('form validation testing', async ({ page }) => {
    // Test empty form submission
    await page.click('[data-testid="submit-button"]');
    
    // Check for validation errors
    await expect(page.locator('[data-testid="first-name-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="message-error"]')).toBeVisible();
    
    // Screenshot validation errors
    await expect(page).toHaveScreenshot('form-validation-errors.png');

    // Test invalid email format
    await page.fill('[data-testid="email"]', 'invalid-email-format');
    await page.blur('[data-testid="email"]');
    
    await expect(page.locator('[data-testid="email-error"]')).toContainText('valid email');
    
    // Test valid email clears error
    await page.fill('[data-testid="email"]', 'valid@example.com');
    await page.blur('[data-testid="email"]');
    
    await expect(page.locator('[data-testid="email-error"]')).not.toBeVisible();

    // Test phone number validation
    await page.fill('[data-testid="phone"]', '123'); // Too short
    await page.blur('[data-testid="phone"]');
    
    await expect(page.locator('[data-testid="phone-error"]')).toBeVisible();
    
    // Valid phone number
    await page.fill('[data-testid="phone"]', '+1-555-123-4567');
    await page.blur('[data-testid="phone"]');
    
    await expect(page.locator('[data-testid="phone-error"]')).not.toBeVisible();

    // Test message length validation
    await page.fill('[data-testid="message"]', 'Short'); // Too short
    await page.blur('[data-testid="message"]');
    
    await expect(page.locator('[data-testid="message-error"]')).toBeVisible();
  });

  test('form accessibility testing', async ({ page }) => {
    // Test keyboard navigation
    await page.keyboard.press('Tab'); // Should focus first input
    
    let focusedElement = await page.evaluate(() => document.activeElement.getAttribute('data-testid'));
    expect(focusedElement).toBe('first-name');

    // Continue tabbing through form
    const expectedTabOrder = [
      'first-name', 'last-name', 'email', 'phone', 
      'company', 'subject', 'message', 'newsletter', 
      'terms', 'submit-button'
    ];

    for (let i = 1; i < expectedTabOrder.length; i++) {
      await page.keyboard.press('Tab');
      focusedElement = await page.evaluate(() => document.activeElement.getAttribute('data-testid'));
      expect(focusedElement).toBe(expectedTabOrder[i]);
    }

    // Test form submission with keyboard
    await page.keyboard.press('Enter');
    
    // Should show validation errors
    await expect(page.locator('[data-testid="first-name-error"]')).toBeVisible();

    // Test aria-labels and descriptions
    const emailInput = page.locator('[data-testid="email"]');
    await expect(emailInput).toHaveAttribute('aria-label');
    await expect(emailInput).toHaveAttribute('aria-describedby');

    // Test focus indicators
    await emailInput.focus();
    await expect(page).toHaveScreenshot('form-focus-indicator.png');
  });

  test('file upload functionality', async ({ page }) => {
    // Check if file upload is present
    const fileInput = page.locator('[data-testid="file-upload"]');
    
    if (await fileInput.isVisible()) {
      // Create a test file
      const testFilePath = 'test-files/test-document.pdf';
      
      // Upload file
      await fileInput.setInputFiles(testFilePath);
      
      // Verify file is selected
      const fileName = await page.locator('[data-testid="file-name"]').textContent();
      expect(fileName).toContain('test-document.pdf');
      
      // Screenshot with file selected
      await expect(page).toHaveScreenshot('form-with-file-upload.png');
    }
  });

  test('form auto-save functionality', async ({ page }) => {
    // Fill some fields
    await page.fill('[data-testid="first-name"]', 'John');
    await page.fill('[data-testid="email"]', 'john@example.com');
    
    // Wait for auto-save (if implemented)
    await page.waitForTimeout(2000);
    
    // Refresh page
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Check if data is restored (if auto-save is implemented)
    const savedFirstName = await page.locator('[data-testid="first-name"]').inputValue();
    const savedEmail = await page.locator('[data-testid="email"]').inputValue();
    
    // This test will pass if auto-save is not implemented
    console.log('Saved data - First Name:', savedFirstName, 'Email:', savedEmail);
  });

  test('form with dynamic fields', async ({ page }) => {
    // Test conditional field visibility
    const businessSelect = page.locator('[data-testid="inquiry-type"]');
    
    if (await businessSelect.isVisible()) {
      // Select business inquiry
      await businessSelect.selectOption('business');
      
      // Check if business-specific fields appear
      await expect(page.locator('[data-testid="company-size"]')).toBeVisible();
      await expect(page.locator('[data-testid="budget"]')).toBeVisible();
      
      // Select personal inquiry
      await businessSelect.selectOption('personal');
      
      // Check if business fields disappear
      await expect(page.locator('[data-testid="company-size"]')).not.toBeVisible();
      await expect(page.locator('[data-testid="budget"]')).not.toBeVisible();
    }
  });

  test('form multi-step functionality', async ({ page }) => {
    // Check if form has multiple steps
    const nextButton = page.locator('[data-testid="next-step"]');
    
    if (await nextButton.isVisible()) {
      // Fill step 1
      await page.fill('[data-testid="first-name"]', 'John');
      await page.fill('[data-testid="last-name"]', 'Doe');
      await page.fill('[data-testid="email"]', 'john@example.com');
      
      await nextButton.click();
      
      // Verify we're on step 2
      await expect(page.locator('[data-testid="step-indicator"]')).toContainText('2');
      
      // Fill step 2
      await page.fill('[data-testid="company"]', 'Test Company');
      await page.selectOption('[data-testid="subject"]', 'Technical Support');
      
      // Go to final step
      await page.click('[data-testid="next-step"]');
      
      // Fill final step
      await page.fill('[data-testid="message"]', 'This is a test message for multi-step form.');
      await page.check('[data-testid="terms"]');
      
      // Submit
      await page.click('[data-testid="submit-button"]');
      
      // Verify success
      await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    }
  });

  test('form error handling and recovery', async ({ page }) => {
    // Fill form with valid data
    await page.fill('[data-testid="first-name"]', 'John');
    await page.fill('[data-testid="last-name"]', 'Doe');
    await page.fill('[data-testid="email"]', 'john@example.com');
    await page.fill('[data-testid="message"]', 'Test message');
    await page.check('[data-testid="terms"]');
    
    // Mock server error
    await page.route('**/api/contact', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Server error' })
      });
    });
    
    // Submit form
    await page.click('[data-testid="submit-button"]');
    
    // Check error message appears
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('error');
    
    // Screenshot error state
    await expect(page).toHaveScreenshot('form-server-error.png');
    
    // Remove mock and retry
    await page.unroute('**/api/contact');
    
    // Retry submission
    await page.click('[data-testid="retry-button"]');
    
    // Should succeed now
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });

  test('form performance and loading states', async ({ page }) => {
    // Monitor form submission time
    const startTime = Date.now();
    
    // Fill form quickly
    await page.fill('[data-testid="first-name"]', 'Speed');
    await page.fill('[data-testid="last-name"]', 'Test');
    await page.fill('[data-testid="email"]', 'speed@test.com');
    await page.fill('[data-testid="message"]', 'Performance test message');
    await page.check('[data-testid="terms"]');
    
    // Submit and measure loading state
    await page.click('[data-testid="submit-button"]');
    
    // Check loading indicator appears
    await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible();
    
    // Wait for completion
    await page.waitForSelector('[data-testid="success-message"]');
    
    const endTime = Date.now();
    const submissionTime = endTime - startTime;
    
    console.log(`Form submission took ${submissionTime}ms`);
    
    // Performance assertion (should complete within 5 seconds)
    expect(submissionTime).toBeLessThan(5000);
  });
});