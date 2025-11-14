#!/usr/bin/env node

/**
 * Visual Consistency Test Script
 * 
 * This script helps execute visual consistency tests for the chat widget
 * against Groww's design system.
 * 
 * Usage:
 *   node scripts/test-visual-consistency.js
 *   node scripts/test-visual-consistency.js --check-tokens
 *   node scripts/test-visual-consistency.js --check-hardcoded
 *   node scripts/test-visual-consistency.js --all
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

// Design token values to validate
const expectedTokens = {
  colors: {
    primary: '#00D09C',
    'primary-hover': '#00B887',
    'primary-active': '#009F75',
    'bg-primary': '#FFFFFF',
    'bg-secondary': '#F9FAFB',
    'bg-tertiary': '#F3F4F6',
    'text-primary': '#222222',
    'text-secondary': '#666666',
    'text-inverse': '#FFFFFF',
    error: '#EF4444',
  },
  spacing: {
    0: '0',
    1: '0.25rem',
    2: '0.5rem',
    3: '0.75rem',
    4: '1rem',
  },
  radius: {
    sm: '0.25rem',
    base: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
  },
};

/**
 * Check if design tokens file exists and contains required tokens
 */
function checkDesignTokens() {
  console.log('\n' + colors.cyan + '='.repeat(80) + colors.reset);
  console.log(colors.cyan + 'Checking Design Tokens' + colors.reset);
  console.log(colors.cyan + '='.repeat(80) + colors.reset);

  const tokensPath = path.join(__dirname, '../src/styles/design-tokens.css');
  
  if (!fs.existsSync(tokensPath)) {
    console.error(colors.red + '❌ Design tokens file not found: ' + tokensPath + colors.reset);
    return false;
  }

  const tokensContent = fs.readFileSync(tokensPath, 'utf-8');
  const issues = [];
  let passed = 0;
  let total = 0;

  // Check color tokens
  console.log('\n' + colors.blue + 'Checking Color Tokens...' + colors.reset);
  for (const [key, value] of Object.entries(expectedTokens.colors)) {
    total++;
    const tokenName = `--color-${key}`;
    const regex = new RegExp(`${tokenName}:\\s*${value.replace('#', '\\#')}`, 'i');
    
    if (regex.test(tokensContent)) {
      console.log(colors.green + `  ✓ ${tokenName}: ${value}` + colors.reset);
      passed++;
    } else {
      console.log(colors.red + `  ✗ ${tokenName}: ${value} (not found or incorrect)` + colors.reset);
      issues.push(`Missing or incorrect token: ${tokenName}`);
    }
  }

  // Check spacing tokens
  console.log('\n' + colors.blue + 'Checking Spacing Tokens...' + colors.reset);
  for (const [key, value] of Object.entries(expectedTokens.spacing)) {
    total++;
    const tokenName = `--spacing-${key}`;
    const regex = new RegExp(`${tokenName}:\\s*${value}`, 'i');
    
    if (regex.test(tokensContent)) {
      console.log(colors.green + `  ✓ ${tokenName}: ${value}` + colors.reset);
      passed++;
    } else {
      console.log(colors.red + `  ✗ ${tokenName}: ${value} (not found or incorrect)` + colors.reset);
      issues.push(`Missing or incorrect token: ${tokenName}`);
    }
  }

  // Check radius tokens
  console.log('\n' + colors.blue + 'Checking Border Radius Tokens...' + colors.reset);
  for (const [key, value] of Object.entries(expectedTokens.radius)) {
    total++;
    const tokenName = `--radius-${key}`;
    const regex = new RegExp(`${tokenName}:\\s*${value}`, 'i');
    
    if (regex.test(tokensContent)) {
      console.log(colors.green + `  ✓ ${tokenName}: ${value}` + colors.reset);
      passed++;
    } else {
      console.log(colors.red + `  ✗ ${tokenName}: ${value} (not found or incorrect)` + colors.reset);
      issues.push(`Missing or incorrect token: ${tokenName}`);
    }
  }

  console.log('\n' + colors.cyan + 'Design Tokens Summary:' + colors.reset);
  console.log(`  Total: ${total}`);
  console.log(`  Passed: ${colors.green}${passed}${colors.reset}`);
  console.log(`  Failed: ${colors.red}${total - passed}${colors.reset}`);

  if (issues.length > 0) {
    console.log('\n' + colors.yellow + 'Issues Found:' + colors.reset);
    issues.forEach(issue => console.log(`  - ${issue}`));
  }

  return issues.length === 0;
}

/**
 * Check for hardcoded color values in CSS files
 */
function checkHardcodedValues() {
  console.log('\n' + colors.cyan + '='.repeat(80) + colors.reset);
  console.log(colors.cyan + 'Checking for Hardcoded Values' + colors.reset);
  console.log(colors.cyan + '='.repeat(80) + colors.reset);

  const componentsDir = path.join(__dirname, '../src/components');
  const cssFiles = [];
  
  function findCSSFiles(dir) {
    const files = fs.readdirSync(dir);
    files.forEach(file => {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory()) {
        findCSSFiles(filePath);
      } else if (file.endsWith('.css')) {
        cssFiles.push(filePath);
      }
    });
  }

  findCSSFiles(componentsDir);

  const hardcodedPatterns = [
    /#[0-9A-Fa-f]{3,6}/g, // Hex colors
    /rgb\([^)]+\)/g, // RGB colors
    /rgba\([^)]+\)/g, // RGBA colors
  ];

  const issues = [];
  let totalFiles = 0;
  let filesWithIssues = 0;

  cssFiles.forEach(filePath => {
    totalFiles++;
    const content = fs.readFileSync(filePath, 'utf-8');
    const relativePath = path.relative(__dirname, filePath);
    const fileIssues = [];

    // Skip design-tokens.css as it's allowed to have hardcoded values
    if (filePath.includes('design-tokens.css')) {
      return;
    }

    hardcodedPatterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) {
        matches.forEach(match => {
          // Allow common CSS values that aren't colors
          if (!match.includes('transparent') && 
              !match.includes('currentColor') &&
              !match.includes('inherit')) {
            fileIssues.push(match);
          }
        });
      }
    });

    if (fileIssues.length > 0) {
      filesWithIssues++;
      console.log(colors.yellow + `\n⚠ ${relativePath}` + colors.reset);
      const uniqueIssues = [...new Set(fileIssues)];
      uniqueIssues.forEach(issue => {
        console.log(`  Found hardcoded value: ${issue}`);
        issues.push({ file: relativePath, value: issue });
      });
    } else {
      console.log(colors.green + `✓ ${relativePath}` + colors.reset);
    }
  });

  console.log('\n' + colors.cyan + 'Hardcoded Values Summary:' + colors.reset);
  console.log(`  Total files checked: ${totalFiles}`);
  console.log(`  Files with issues: ${colors.red}${filesWithIssues}${colors.reset}`);
  console.log(`  Files clean: ${colors.green}${totalFiles - filesWithIssues}${colors.reset}`);

  if (issues.length > 0) {
    console.log('\n' + colors.yellow + 'Recommendation:' + colors.reset);
    console.log('  Replace hardcoded values with design tokens from design-tokens.css');
  }

  return issues.length === 0;
}

/**
 * Generate test report template
 */
function generateTestReport() {
  console.log('\n' + colors.cyan + '='.repeat(80) + colors.reset);
  console.log(colors.cyan + 'Generating Test Report Template' + colors.reset);
  console.log(colors.cyan + '='.repeat(80) + colors.reset);

  const reportPath = path.join(__dirname, '../visual-consistency-test-report.md');
  
  const report = `# Visual Consistency Test Report

**Date:** ${new Date().toISOString().split('T')[0]}
**Tester:** [Your Name]
**Browser:** [Browser and Version]
**Screen Size:** [Width × Height]

## Test Results

### Design Tokens
- [ ] All required tokens are defined
- [ ] Token values match Groww's design system
- [ ] No hardcoded values found in components

### Colors
- [ ] Primary Green (#00D09C): [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Background Colors: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Text Colors: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Semantic Colors: [ ] Pass [ ] Fail - Notes: [Notes]

### Typography
- [ ] Font Family: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Font Sizes: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Font Weights: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Line Heights: [ ] Pass [ ] Fail - Notes: [Notes]

### Spacing
- [ ] Component Spacing: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Layout Spacing: [ ] Pass [ ] Fail - Notes: [Notes]

### Components
- [ ] Chat Widget: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Header: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Messages: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Input: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Button: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Sources Section: [ ] Pass [ ] Fail - Notes: [Notes]

### Responsive Design
- [ ] Mobile (≤640px): [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Tablet (641px-1024px): [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Desktop (1025px+): [ ] Pass [ ] Fail - Notes: [Notes]

### Accessibility
- [ ] Color Contrast: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Focus Indicators: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Keyboard Navigation: [ ] Pass [ ] Fail - Notes: [Notes]
- [ ] Screen Reader Support: [ ] Pass [ ] Fail - Notes: [Notes]

### Visual Comparison
- [ ] Widget matches Groww's visual style: [ ] Pass [ ] Fail
- [ ] Colors match Groww website: [ ] Pass [ ] Fail
- [ ] Typography matches Groww website: [ ] Pass [ ] Fail
- [ ] Spacing matches Groww website: [ ] Pass [ ] Fail

## Overall Assessment
[ ] Pass - Widget is visually consistent with Groww design system
[ ] Fail - Widget needs adjustments to match Groww design system

## Issues Found
1. [Issue description]
2. [Issue description]

## Recommendations
1. [Recommendation]
2. [Recommendation]

## Screenshots
[Attach screenshots comparing widget with Groww website]

---

**Next Steps:**
1. Complete manual visual inspection using browser dev tools
2. Compare widget with Groww website (https://groww.in)
3. Document any discrepancies
4. Update design tokens if needed
5. Re-run this script to verify fixes
`;

  fs.writeFileSync(reportPath, report, 'utf-8');
  console.log(colors.green + `✓ Test report template generated: ${reportPath}` + colors.reset);
  console.log(colors.blue + '\nFill out the report after completing manual visual inspection.' + colors.reset);
}

/**
 * Display manual testing checklist
 */
function displayChecklist() {
  console.log('\n' + colors.cyan + '='.repeat(80) + colors.reset);
  console.log(colors.cyan + 'Manual Visual Consistency Testing Checklist' + colors.reset);
  console.log(colors.cyan + '='.repeat(80) + colors.reset);

  const checklist = `
${colors.yellow}IMPORTANT:${colors.reset} Visual consistency testing requires manual inspection.
This script helps validate code, but you must manually compare the widget with Groww's website.

${colors.blue}Steps to follow:${colors.reset}

1. ${colors.green}Setup${colors.reset}
   - Open Groww website: https://groww.in
   - Open chat widget in development environment
   - Have browser dev tools ready (F12)

2. ${colors.green}Color Verification${colors.reset}
   - Use browser color picker to extract colors from Groww website
   - Compare with widget colors using dev tools
   - Verify primary green (#00D09C) matches exactly
   - Check background, text, and semantic colors

3. ${colors.green}Typography Verification${colors.reset}
   - Inspect font families on Groww website
   - Compare font sizes and weights
   - Verify line heights match

4. ${colors.green}Spacing Verification${colors.reset}
   - Measure spacing on Groww website
   - Compare with widget spacing
   - Verify consistency

5. ${colors.green}Component Comparison${colors.reset}
   - Compare similar components (buttons, inputs, cards)
   - Note visual differences
   - Document acceptable variations

6. ${colors.green}Responsive Testing${colors.reset}
   - Test on different screen sizes
   - Verify mobile, tablet, desktop layouts
   - Check breakpoints

7. ${colors.green}Accessibility Testing${colors.reset}
   - Test keyboard navigation
   - Verify focus indicators
   - Check color contrast ratios
   - Test with screen reader

${colors.yellow}For detailed test procedures, see: docs/VISUAL_CONSISTENCY_TEST.md${colors.reset}
`;

  console.log(checklist);
}

/**
 * Main function
 */
function main() {
  const args = process.argv.slice(2);
  const checkTokens = args.includes('--check-tokens') || args.includes('--all');
  const checkHardcoded = args.includes('--check-hardcoded') || args.includes('--all');
  const generateReport = args.includes('--generate-report') || args.includes('--all');
  const showChecklist = args.includes('--checklist') || args.includes('--all') || args.length === 0;

  console.log(colors.cyan + '\n' + '='.repeat(80) + colors.reset);
  console.log(colors.cyan + 'Visual Consistency Test Script' + colors.reset);
  console.log(colors.cyan + '='.repeat(80) + colors.reset);

  let allPassed = true;

  if (checkTokens) {
    const tokensPassed = checkDesignTokens();
    allPassed = allPassed && tokensPassed;
  }

  if (checkHardcoded) {
    const hardcodedPassed = checkHardcodedValues();
    allPassed = allPassed && hardcodedPassed;
  }

  if (generateReport) {
    generateTestReport();
  }

  if (showChecklist) {
    displayChecklist();
  }

  console.log('\n' + colors.cyan + '='.repeat(80) + colors.reset);
  if (allPassed && (checkTokens || checkHardcoded)) {
    console.log(colors.green + '✓ All automated checks passed!' + colors.reset);
  } else if (checkTokens || checkHardcoded) {
    console.log(colors.yellow + '⚠ Some issues found. Please review and fix.' + colors.reset);
  }
  console.log(colors.cyan + '='.repeat(80) + colors.reset);

  console.log('\n' + colors.blue + 'Usage:' + colors.reset);
  console.log('  node scripts/test-visual-consistency.js --all');
  console.log('  node scripts/test-visual-consistency.js --check-tokens');
  console.log('  node scripts/test-visual-consistency.js --check-hardcoded');
  console.log('  node scripts/test-visual-consistency.js --generate-report');
  console.log('  node scripts/test-visual-consistency.js --checklist');
}

// Run if executed directly
main();

export { checkDesignTokens, checkHardcodedValues, generateTestReport };

