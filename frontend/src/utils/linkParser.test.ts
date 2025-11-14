/**
 * Tests for linkParser utility
 * 
 * Note: This is a test file for reference. Actual tests would be in a proper test framework.
 */

import { parseLinks, isGrowwUrl, getSourceTypeFromUrl, getDomainName } from './linkParser';

// Test cases (for manual verification)

const testCases = [
  {
    name: 'Plain URL',
    input: 'Check out https://groww.in/mutual-funds for more info.',
    expected: 'Should parse URL and mark as Groww link',
  },
  {
    name: 'Markdown link',
    input: 'Visit [Groww Mutual Funds](https://groww.in/mutual-funds) for details.',
    expected: 'Should parse markdown link with custom text',
  },
  {
    name: 'Multiple URLs',
    input: 'See https://groww.in and https://sebi.gov.in for more.',
    expected: 'Should parse both URLs separately',
  },
  {
    name: 'No URLs',
    input: 'This is plain text with no links.',
    expected: 'Should return single text part',
  },
  {
    name: 'Mixed content',
    input: 'Text before https://example.com and [link](https://groww.in) after.',
    expected: 'Should handle both markdown and plain URLs',
  },
];

// Helper function to test
export const runTests = () => {
  console.log('Running linkParser tests...');
  
  testCases.forEach((testCase) => {
    const result = parseLinks(testCase.input);
    console.log(`\n${testCase.name}:`);
    console.log('Input:', testCase.input);
    console.log('Parsed:', result);
    console.log('Expected:', testCase.expected);
  });
  
  // Test URL detection
  console.log('\nURL Detection Tests:');
  console.log('isGrowwUrl("https://groww.in/test"):', isGrowwUrl('https://groww.in/test'));
  console.log('isGrowwUrl("https://example.com"):', isGrowwUrl('https://example.com'));
  
  // Test source type detection
  console.log('\nSource Type Tests:');
  console.log('getSourceTypeFromUrl("https://groww.in/test"):', getSourceTypeFromUrl('https://groww.in/test'));
  console.log('getSourceTypeFromUrl("https://sebi.gov.in/test"):', getSourceTypeFromUrl('https://sebi.gov.in/test'));
  console.log('getDomainName("https://www.groww.in/test"):', getDomainName('https://www.groww.in/test'));
};

