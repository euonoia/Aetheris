## 1. Title (Frontend Refactor: Canvas-Based Live Preview, Landing Page Expansion, and Dashboard Tracking Updates - 2026-07-18)

## 2. Summary
This update significantly enhances the frontend with three major improvements: (1) Converting the LiveFramePreview component from `<img>` to `<canvas>` for better control over frame rendering, (2) Enabling and styling the complete landing page with HowItWorks, SystemModules, Benefits, and other marketing sections, and (3) Refactoring the DashboardPage to display active vehicle tracks with real-time telemetry and progress indicators. Additionally, new dependencies (recharts and embla-carousel-react) are added to support charting and carousel functionality.

## 3. Frontend Changes
- Framework/library used: React + TypeScript
- Files/components affected:
  - `frontend/src/components/LiveFramePreview.tsx` (refactored to use Canvas API)
  - `frontend/src/pages/DashboardPage.tsx` (tracking UI overhaul)
  - `frontend/src/pages/landing/LandingPage.tsx` (uncommented sections)
  - `frontend/src/pages/landing/components/Hero.tsx` (button styling fixes, route links)
  - `frontend/src/pages/landing/components/KeyFeatures.tsx` (badge and icon styling)
  - `frontend/src/pages/landing/components/Navbar.tsx` (route navigation updates, button styling)
  - `frontend/src/pages/landing/components/SystemOverview.tsx` (badge styling, section background)
  - `frontend/src/App.tsx` (minor formatting)
  - `frontend/src/components/ui/button.tsx` (modified)

- What changed:
  - **LiveFramePreview Component**: Converted from `<img>` tag to `<canvas>` element using React hooks (`useRef`, `useEffect`). The component now:
    - Uses `Image` object to load base64 JPEG frames
    - Dynamically sets canvas resolution to match incoming image dimensions
    - Draws frames directly onto canvas context
    - Provides better control over rendering and potential for future overlays
  - **DashboardPage**: 
    - Removed hardcoded violation detection UI
    - Added `progressVariantBadge` type for mapping job status to badge variants
    - Created tracking status display showing processing progress percentage
    - Replaced static detection result panel with live active tracks table displaying: Track ID, Vehicle Type, Confidence, Last Frame, and Duration
    - Improved conditional rendering for loading and empty states
    - Removed console.log debug statement
    - Reorganized layout and spacing for better readability
  - **Landing Page Components**: Uncommented and re-enabled all previously commented sections (HowItWorks, SystemModules, AIHighlight, DashboardPreview, Benefits, AboutBarangay, Contact, Footer)
  - **Hero Component**: Fixed button styling with proper flex layout and icon spacing; updated navigation links
  - **KeyFeatures & SystemOverview**: Updated badge styling from `outline`/`secondary` to `default`; changed icon backgrounds from `bg-primary/10` to `bg-secondary` with `text-accent`
  - **Navbar**: Updated routes from `/app` to `/dashboard`; improved button styling consistency

- Screenshots or references (optional): None

## 4. Backend Changes
- Language/framework used: N/A
- Files/modules affected: N/A
- What changed: None
- API endpoints added/modified: None

## 5. API Reference

| Method | Endpoint | Description | Request | Response |
| ------ | -------- | ----------- | ------- | -------- |
| N/A | N/A | No API changes made | N/A | N/A |

## 6. Database Changes
- Tables/collections affected: None
- Migration/schema changes: None

## 7. Testing Notes
- How this was tested: Manual verification of component rendering and navigation
- Known issues or edge cases: 
  - Canvas rendering depends on Image.onload event; timing issues possible if frame updates are too rapid
  - Active tracks table assumes `activeTrackDetails` is populated from WebSocket messages
  - Progress percentage display relies on `inferredStatus?.progress_percentage` being available

## 8. Known Issues / TODOs
- Canvas may require error handling for failed image loads
- Track table styling uses inline styles; consider moving to Tailwind classes for consistency
- Verify all imported components (HowItWorks, SystemModules, etc.) are properly exported from their modules
- Test responsive behavior of the new landing page sections on mobile devices

## 9. Related Files
- `frontend/package.json` (dependencies updated)
- `frontend/src/components/LiveFramePreview.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/landing/LandingPage.tsx`
- `frontend/src/pages/landing/components/Hero.tsx`
- `frontend/src/pages/landing/components/KeyFeatures.tsx`
- `frontend/src/pages/landing/components/Navbar.tsx`
- `frontend/src/pages/landing/components/SystemOverview.tsx`
- `frontend/src/App.tsx`
