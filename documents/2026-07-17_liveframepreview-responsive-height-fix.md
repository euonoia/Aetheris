## 1. Title (LiveFramePreview responsive height fix - 2026-07-17)

## 2. Summary
Updated the live frame preview component to render the incoming image with a responsive height and simplified markup. This change removes the placeholder container and waiting text, ensuring the live monitor frame displays correctly when data is available.

## 3. Frontend Changes
- Framework/library used: React
- Files/components affected: `frontend/src/components/LiveFramePreview.tsx`
- What changed:
  - Removed the `containerStyle` wrapper and waiting text markup.
  - Simplified the component to return only the live frame image when a message exists.
  - Set the frame image `height` to `auto` to preserve aspect ratio and support responsive rendering.
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
- How this was tested: Manual verification of the live preview component render behavior
- Known issues or edge cases: None

## 8. Known Issues / TODOs
- None

## 9. Related Files
- `frontend/src/components/LiveFramePreview.tsx`
