---
name: Nurse Monitoring Dashboard
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#3d4947'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#6d7a77'
  outline-variant: '#bcc9c6'
  surface-tint: '#006a61'
  primary: '#00685f'
  on-primary: '#ffffff'
  primary-container: '#008378'
  on-primary-container: '#f4fffc'
  inverse-primary: '#6bd8cb'
  secondary: '#0058be'
  on-secondary: '#ffffff'
  secondary-container: '#2170e4'
  on-secondary-container: '#fefcff'
  tertiary: '#595c5e'
  on-tertiary: '#ffffff'
  tertiary-container: '#727577'
  on-tertiary-container: '#fbfdff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#89f5e7'
  primary-fixed-dim: '#6bd8cb'
  on-primary-fixed: '#00201d'
  on-primary-fixed-variant: '#005049'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a42'
  on-secondary-fixed-variant: '#004395'
  tertiary-fixed: '#e0e3e5'
  tertiary-fixed-dim: '#c4c7c9'
  on-tertiary-fixed: '#191c1e'
  on-tertiary-fixed-variant: '#444749'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-mono:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '700'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  container-padding: 24px
  gutter: 16px
  widget-gap: 20px
  base-margin: 8px
---

## Brand & Style

The design system is engineered for high-stakes medical environments, specifically focused on nurse monitoring and fluid management. The brand personality is **clinical, precise, and dependable**. It aims to evoke a sense of calm authority, ensuring that critical data is processed quickly without cognitive overload.

The visual style is **Corporate / Modern** with a strong emphasis on data density. By utilizing a "Clinical Light" aesthetic, the design system minimizes eye strain during 12-hour shifts through low-vibrancy backgrounds and highly legible typography. Information hierarchy is prioritized above all else, ensuring that a nurse can distinguish between routine monitoring and emergency intervention at a glance.

## Colors

This design system utilizes a primary teal (#0D9488) to maintain brand continuity, paired with a clinical palette designed for professional environments.

- **Primary Teal:** Used for primary actions, active navigation states, and brand-critical elements.
- **Clinical Blue/White:** The background uses a soft Slate-50 to Slate-100 wash to reduce the harsh glare of pure white screens.
- **Data Visualization (High Contrast):**
    - **Safe:** A vivid emerald green for stable fluid levels.
    - **Warning:** A warm amber for monitoring trends that require attention.
    - **Critical:** A sharp, high-visibility red reserved exclusively for immediate life-safety alerts.
- **Neutrals:** Deep slates and grays are used for secondary text and structural borders to maintain a professional, organized appearance.

## Typography

The design system relies exclusively on **Inter** to ensure maximum legibility across different monitor resolutions. 

To handle data-heavy dashboards, the system employs **tabular numshat** (tnum) for all numerical data, ensuring that columns of numbers align perfectly for quick scanning. Line heights are kept tight but breathable to maximize the amount of information visible "above the fold" on desktop screens. Labels use uppercase with slight letter spacing to differentiate them from interactive body text.

## Layout & Spacing

This design system uses a **Fluid Grid** model optimized for wide-screen desktop monitoring. The layout is based on a 12-column grid that allows for flexible widget placement.

- **Data Density:** Spacing is built on a 4px baseline shift. Most internal component padding is 8px or 12px to allow for a "data-heavy" interface without feeling cluttered.
- **Desktop Breakpoints:** The primary experience is designed for 1440px+ viewports, with a secondary tablet-landscape optimization.
- **Margins:** Standard outer container margins are set to 24px, while internal gutters between data cards are set to 16px to maintain a distinct separation of patient records.

## Elevation & Depth

To maintain a clean, clinical aesthetic, the design system avoids heavy shadows. Hierarchy is instead established through **Tonal Layers** and **Low-Contrast Outlines**.

- **Surface Levels:** The main background is a soft blue-gray. Interactive cards and "widgets" sit on pure white (#FFFFFF) surfaces.
- **Outlines:** Use 1px borders in a light Slate-200 to define containers. 
- **Focus States:** When a specific patient record is selected, a 2px primary teal border is applied rather than a shadow, ensuring the focus is unambiguous in high-pressure situations.

## Shapes

The design system uses a **Soft** shape language (Level 1). 

Corners are slightly rounded (4px to 8px) to provide a modern feel while maintaining a professional, structured look. This subtle rounding helps to distinguish individual UI modules without wasting the screen real estate that "Pill" shapes often consume. Interactive elements like buttons and inputs follow this 4px standard, while larger dashboard containers use 8px.

## Components

### Buttons & Inputs
Buttons use the primary teal for "Save" or "Confirm" actions. Input fields use a clear 1px border with a soft blue background on hover to indicate interactivity. In the monitoring context, "Critical" action buttons (e.g., Stop Pump) use the Semantic Red.

### Monitoring Cards
Patient monitoring cards are the core component. They feature a header with the patient name, a large "Data-Mono" readout for the most critical metric (e.g., fluid volume), and a sparkline trend graph.

### Status Chips
Status indicators use high-contrast text on a light tinted background of the same color (e.g., Dark Green text on light green background) for "Safe" states, ensuring color-blind accessibility by combining color with clear text labels.

### Data Tables
Tables are designed for high density. Rows have a fixed height of 40px with subtle zebra-striping using the clinical-blue background color to guide the eye across wide rows of telemetry data.

### Alerts
Sticky alert banners appear at the top of the dashboard. Critical alerts use a pulsing red left-border to draw immediate attention without obscuring the rest of the monitoring data.