# Visual Consistency Test - Groww Design System

This document outlines the visual consistency testing procedures for the FAQ Chat Widget against Groww's design system.

## Test Overview

**Purpose**: Ensure the chat widget maintains visual consistency with Groww's design system across all components and states.

**Last Updated**: 2024-11-14

## Pre-Testing Checklist

- [ ] Design tokens are properly defined in `frontend/src/styles/design-tokens.css`
- [ ] All components use design tokens (no hardcoded values)
- [ ] Design tokens documentation is up to date (`docs/DESIGN_TOKENS.md`)
- [ ] Browser dev tools are available for inspection

## Test Categories

### 1. Color Consistency

#### 1.1 Primary Brand Colors
- [ ] **Primary Green (#00D09C)**
  - Used in: Chat header background, user message bubbles, primary buttons
  - Verify: Exact color match with Groww website
  - Test: Compare using browser color picker on Groww website vs widget

- [ ] **Primary Hover (#00B887)**
  - Used in: Button hover states, link hover states
  - Verify: Smooth transition, appropriate contrast

- [ ] **Primary Active (#009F75)**
  - Used in: Button active/pressed states
  - Verify: Visual feedback on interaction

#### 1.2 Background Colors
- [ ] **Chat Background (#FFFFFF)**
  - Verify: Clean white background, no tinting

- [ ] **Message Bot Background (#F3F4F6)**
  - Verify: Subtle gray, good contrast with text

- [ ] **Input Background (#F9FAFB)**
  - Verify: Light gray, distinguishable from chat background

#### 1.3 Text Colors
- [ ] **Primary Text (#222222)**
  - Verify: High contrast (15.8:1) on white background
  - Test: WCAG AA compliance

- [ ] **Secondary Text (#666666)**
  - Verify: Readable but less prominent than primary text

- [ ] **Inverse Text (#FFFFFF)**
  - Verify: Readable on primary green background
  - Note: May need larger font size for WCAG compliance

#### 1.4 Semantic Colors
- [ ] **Error Color (#EF4444)**
  - Used in: Error messages, error borders
  - Verify: Clearly distinguishable, accessible contrast

- [ ] **Success Color (#10B981)**
  - Verify: Positive feedback color matches Groww's success indicators

### 2. Typography Consistency

#### 2.1 Font Family
- [ ] **Primary Font Stack**
  - Verify: System font stack matches Groww's typography
  - Test: Render text and compare with Groww website

#### 2.2 Font Sizes
- [ ] **Base Size (16px)**
  - Verify: Standard readable size for body text

- [ ] **Header Size (18px)**
  - Verify: Appropriate hierarchy for chat header

- [ ] **Small Text (12px)**
  - Verify: Timestamps and metadata are readable

- [ ] **Large Text (20px+)**
  - Verify: Headers and important messages stand out

#### 2.3 Font Weights
- [ ] **Normal (400)**
  - Verify: Body text weight matches Groww

- [ ] **Medium (500)**
  - Verify: Used for emphasis appropriately

- [ ] **Semibold (600)**
  - Verify: Headers and important labels

#### 2.4 Line Heights
- [ ] **Normal (1.5)**
  - Verify: Comfortable reading for body text

- [ ] **Relaxed (1.625)**
  - Verify: Used for longer content blocks

### 3. Spacing Consistency

#### 3.1 Component Spacing
- [ ] **Chat Widget Padding (16px)**
  - Verify: Consistent internal spacing

- [ ] **Message Gap (12px)**
  - Verify: Messages are visually separated but not too far

- [ ] **Bubble Padding (12px vertical, 16px horizontal)**
  - Verify: Comfortable text padding within bubbles

#### 3.2 Layout Spacing
- [ ] **Widget Margins**
  - Verify: Proper spacing from viewport edges

- [ ] **Section Spacing**
  - Verify: Header, body, footer have appropriate gaps

### 4. Border Radius Consistency

#### 4.1 Widget Radius
- [ ] **Widget Border Radius (12px)**
  - Verify: Matches Groww's card/container styling

#### 4.2 Component Radius
- [ ] **Message Bubble Radius (8px)**
  - Verify: Rounded but not too circular

- [ ] **Input Radius (8px)**
  - Verify: Consistent with other input elements

- [ ] **Button Radius (6px)**
  - Verify: Slightly less rounded than bubbles

### 5. Shadow Consistency

#### 5.1 Widget Shadow
- [ ] **Widget Shadow (xl)**
  - Verify: Elevation matches Groww's floating elements
  - Test: Compare depth with Groww's modals/cards

#### 5.2 Component Shadows
- [ ] **Button Shadow (base)**
  - Verify: Subtle elevation on interactive elements

- [ ] **Bubble Shadow (sm)**
  - Verify: Minimal shadow for depth without distraction

### 6. Component-Specific Tests

#### 6.1 Chat Widget Container
- [ ] **Dimensions**
  - Width: 400px (standard desktop)
  - Height: 600px (or 80vh max)
  - Verify: Matches Groww's modal/card sizing patterns

- [ ] **Positioning**
  - Bottom-right: 24px from edges
  - Verify: Consistent with Groww's floating elements

#### 6.2 Chat Header
- [ ] **Background Color**
  - Primary green (#00D09C)
  - Verify: Exact match with Groww's primary color

- [ ] **Text Color**
  - White (#FFFFFF)
  - Verify: Good contrast, readable

- [ ] **Typography**
  - Size: 18px, Weight: 600
  - Verify: Matches Groww's header styling

#### 6.3 Message Bubbles

##### User Messages
- [ ] **Background**: Primary green (#00D09C)
- [ ] **Text**: White (#FFFFFF)
- [ ] **Alignment**: Right
- [ ] **Max Width**: 85%
- [ ] **Padding**: 12px vertical, 16px horizontal
- [ ] **Border Radius**: 8px

##### Assistant Messages
- [ ] **Background**: Light gray (#F3F4F6)
- [ ] **Text**: Dark gray (#222222)
- [ ] **Alignment**: Left
- [ ] **Max Width**: 85%
- [ ] **Padding**: 12px vertical, 16px horizontal
- [ ] **Border Radius**: 8px

#### 6.4 Chat Input
- [ ] **Background**: Light gray (#F9FAFB)
- [ ] **Border**: Gray (#E5E7EB)
- [ ] **Focus Border**: Primary green (#00D09C)
- [ ] **Border Radius**: 8px
- [ ] **Padding**: 12px
- [ ] **Font Size**: 16px

#### 6.5 Floating Button
- [ ] **Size**: 60px × 60px
- [ ] **Background**: Primary green (#00D09C)
- [ ] **Icon**: White, 28px
- [ ] **Border Radius**: 50% (fully rounded)
- [ ] **Shadow**: Base shadow
- [ ] **Position**: Bottom-right, 24px from edges

#### 6.6 Source Links
- [ ] **Link Color**: Secondary blue (#5367FC)
- [ ] **Hover Color**: Darker blue (#4257E8)
- [ ] **Underline**: Yes, with proper offset
- [ ] **Groww Links**: Special indicator (↗)

### 7. Responsive Design Tests

#### 7.1 Mobile (≤640px)
- [ ] **Widget**: Full screen
- [ ] **Border Radius**: 0 (no rounded corners)
- [ ] **Spacing**: Adjusted for smaller screen
- [ ] **Font Sizes**: Slightly reduced

#### 7.2 Tablet (641px-1024px)
- [ ] **Widget Width**: 360px
- [ ] **Widget Height**: 500px
- [ ] **Spacing**: Proportional reduction

#### 7.3 Desktop (1025px+)
- [ ] **Widget Width**: 400px (standard)
- [ ] **Widget Height**: 600px
- [ ] **Spacing**: Standard values

### 8. State-Based Tests

#### 8.1 Loading States
- [ ] **Loading Indicator**: Matches Groww's loading patterns
- [ ] **Animation**: Smooth, not jarring
- [ ] **Color**: Uses primary green

#### 8.2 Error States
- [ ] **Error Color**: Red (#EF4444)
- [ ] **Error Icon**: Visible, accessible
- [ ] **Error Message**: Clear, actionable

#### 8.3 Hover States
- [ ] **Buttons**: Color transition to hover state
- [ ] **Links**: Underline thickness increase
- [ ] **Source Items**: Background color change

#### 8.4 Focus States
- [ ] **Focus Outline**: Primary green (#00D09C)
- [ ] **Outline Width**: 2px
- [ ] **Outline Offset**: 2px
- [ ] **Visible**: Always visible for accessibility

### 9. Accessibility Tests

#### 9.1 Color Contrast
- [ ] **Text on White**: 15.8:1 (exceeds WCAG AAA)
- [ ] **White on Green**: 2.9:1 (WCAG AA for large text)
- [ ] **Gray Text on Gray**: 14.2:1 (exceeds WCAG AAA)

#### 9.2 Focus Indicators
- [ ] **All Interactive Elements**: Visible focus indicators
- [ ] **Focus Color**: Primary green
- [ ] **Keyboard Navigation**: All elements accessible

### 10. Visual Regression Testing

#### 10.1 Screenshot Comparison
- [ ] **Baseline Screenshots**: Capture at different screen sizes
- [ ] **Component Screenshots**: Individual component states
- [ ] **Comparison Tool**: Use visual regression testing tool

#### 10.2 Browser Testing
- [ ] **Chrome**: Latest version
- [ ] **Firefox**: Latest version
- [ ] **Safari**: Latest version
- [ ] **Edge**: Latest version

## Test Execution Steps

1. **Setup**
   - Open Groww website (https://groww.in)
   - Open chat widget in development environment
   - Have browser dev tools ready

2. **Color Verification**
   - Use browser color picker to extract colors from Groww website
   - Compare with widget colors using dev tools
   - Document any discrepancies

3. **Typography Verification**
   - Inspect font families on Groww website
   - Compare font sizes and weights
   - Verify line heights

4. **Spacing Verification**
   - Measure spacing on Groww website
   - Compare with widget spacing
   - Verify consistency

5. **Component Comparison**
   - Compare similar components (buttons, inputs, cards)
   - Note visual differences
   - Document acceptable variations

## Expected Results

### ✅ Pass Criteria
- All colors match Groww's design system (within acceptable tolerance)
- Typography matches Groww's font stack and sizing
- Spacing follows Groww's spacing scale
- Components visually align with Groww's component library
- Accessibility standards are met (WCAG AA minimum)

### ⚠️ Acceptable Variations
- Minor color variations due to display calibration
- Font rendering differences across browsers
- Shadow variations due to browser implementation

### ❌ Fail Criteria
- Significant color mismatches (>5% difference)
- Typography that doesn't match Groww's style
- Spacing that doesn't follow Groww's scale
- Components that look significantly different from Groww's design

## Test Results Template

```
Date: [Date]
Tester: [Name]
Browser: [Browser and Version]
Screen Size: [Width × Height]

### Colors
- Primary Green: [ ] Pass [ ] Fail - Notes: [Notes]
- Background Colors: [ ] Pass [ ] Fail - Notes: [Notes]
- Text Colors: [ ] Pass [ ] Fail - Notes: [Notes]

### Typography
- Font Family: [ ] Pass [ ] Fail - Notes: [Notes]
- Font Sizes: [ ] Pass [ ] Fail - Notes: [Notes]
- Font Weights: [ ] Pass [ ] Fail - Notes: [Notes]

### Spacing
- Component Spacing: [ ] Pass [ ] Fail - Notes: [Notes]
- Layout Spacing: [ ] Pass [ ] Fail - Notes: [Notes]

### Components
- Chat Widget: [ ] Pass [ ] Fail - Notes: [Notes]
- Header: [ ] Pass [ ] Fail - Notes: [Notes]
- Messages: [ ] Pass [ ] Fail - Notes: [Notes]
- Input: [ ] Pass [ ] Fail - Notes: [Notes]
- Button: [ ] Pass [ ] Fail - Notes: [Notes]

### Responsive
- Mobile: [ ] Pass [ ] Fail - Notes: [Notes]
- Tablet: [ ] Pass [ ] Fail - Notes: [Notes]
- Desktop: [ ] Pass [ ] Fail - Notes: [Notes]

### Accessibility
- Color Contrast: [ ] Pass [ ] Fail - Notes: [Notes]
- Focus Indicators: [ ] Pass [ ] Fail - Notes: [Notes]

### Overall Assessment
[ ] Pass - Widget is visually consistent with Groww design system
[ ] Fail - Widget needs adjustments to match Groww design system

### Issues Found
1. [Issue description]
2. [Issue description]
...

### Recommendations
1. [Recommendation]
2. [Recommendation]
...
```

## Maintenance

### Regular Reviews
- **Quarterly**: Full visual consistency review
- **After Design Updates**: Verify consistency after Groww updates
- **Before Releases**: Quick visual check

### Update Process
1. Review Groww website for design changes
2. Update design tokens if needed
3. Update components to use new tokens
4. Run visual consistency tests
5. Document changes

## Resources

- [Groww Website](https://groww.in) - Reference for visual inspection
- [Design Tokens Documentation](./DESIGN_TOKENS.md) - Token definitions
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) - Accessibility standards
- [Browser Dev Tools](https://developer.mozilla.org/en-US/docs/Learn/Common_questions/What_are_browser_developer_tools) - Inspection tools

---

**Note**: This test should be performed manually by comparing the widget with Groww's actual website. Automated visual regression testing can supplement but not replace manual visual inspection.

