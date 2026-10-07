# Career Compass - Configuration Guide

This guide explains how to manage settings, update the underlying SAS models, and configure data for the Career Compass web application.

## 1. Updating the SAS Model Coefficients
The core logic for predicting the probability of a high salary hike is derived from a SAS Logistic Regression model.
If you retrain the model with new data in SAS, you will need to update the coefficients.

**File:** `src/pages/Simulator.tsx`
**Function:** `calculateProbability(s: number[])`

```typescript
const calculateProbability = (s: number[]) => {
  const [dash, math, aiml, big, code] = s
  // UPDATE THESE COEFFICIENTS based on your SAS PROC LOGISTIC output
  const z = -26.2236 
          + 1.821 * math 
          + 1.3547 * dash 
          + 1.2639 * aiml 
          + 0.9961 * big 
          + 0.609 * code;

  return Math.round((1 / (1 + Math.exp(-z))) * 100)
}
```
*Note: The Upskilling ROI (Skill ROI Recommendation) dynamically calculates the highest delta based on these coefficients. You do not need to update the ROI logic when you update coefficients.*

## 2. Managing Salary & Career Ladder Data
The Salary Estimator uses baseline metrics, role premiums, and experience multipliers.

**File:** `src/pages/Salary.tsx`
**Variable:** `salary` (inside the `useMemo` hook)

Update the dictionaries if market data shifts:
```typescript
const premiums: Record<string, number> = { DA: -3.21, BA: -1.3, DE: 1.85, DS: 3.53, MLE: 0, ARCH: 10.95 }
const seniorBumps: Record<string, number> = { DA: 0.79, BA: 0.72, DE: 2.57, DS: 5.1, MLE: 2.5, ARCH: 0 }
// Update the baseline scalar (11.2) and experience multiplier (1.5115) here
```

## 3. Editing Copy and Data Constants
All hardcoded labels, dropdown options, and copy content are centralised in the constants file.

**File:** `src/data/constants.ts`

- `competencyFields`: The 5 technical pillars used in the Simulator. Formatted as `[Name, Low Label, Mid Label, High Label, Default Value]`.
- `roles`: The job titles populated in the Salary Estimator dropdown.
- `matrixItems`: The Skill Gap / Market Demand Matrix cards content.
- `personas`: The Senior Leadership Personas clustering results.

## 4. UI/UX Design Configuration
Colors, breakpoints, and CSS layouts are managed globally via standard CSS variables.

**File:** `src/App.css`

At the top of the file, you can manage the core theme colors:
```css
:root { 
  --ink: #0a0a0a;   /* Primary dark color for text/bars/active states */
  --muted: #71717a; /* Secondary text and disabled states */
  --line: #e4e4e7;  /* Borders and dividers */
  --low: #f6f2f7;   /* Backgrounds for cards and inputs */
}
```
Fonts are configured in `src/index.css` via a Google Fonts import (`Geist` and `JetBrains Mono`).

## 5. Development Commands
The project is built with Vite + React + TypeScript.

- **Start Local Server:** `npm run dev`
- **Build for Production:** `npm run build`
- **Lint Code:** `npm run lint`
