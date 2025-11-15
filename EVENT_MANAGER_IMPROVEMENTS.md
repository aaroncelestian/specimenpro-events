# Event Manager UI Improvements

## Summary of Enhancements

### 1. Date/Time Fields ✅
- **Start Date & End Date** remain as text entry fields
- Enter dates in any format (RFC, ISO, or simple date format)
- Example formats:
  - RFC: "Thu, 13 Nov 2025 00:00:00 GMT"
  - ISO: "2025-11-13T00:00:00Z"
  - Simple: "2025-11-13"

### 2. Enhanced Specimen Editor ✅
- **Larger dialog window**: Increased from 500x700 to 700x900
- **Bigger text fields**:
  - Description: 5 lines (was 3)
  - Fun Facts: 6 lines (was 4)
  - Story: 10 lines (was 6)
  - Composition: 4 lines (was 3)
- All text fields now have `wrap=tk.WORD` for better text editing

### 3. Unicode Subscript/Superscript Buttons ✅
- **Composition field** now has quick-insert buttons
- **Subscripts**: ₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉
- **Superscripts**: ⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹ ⁺ ⁻
- Click any button to insert the character at cursor position
- Makes entering chemical formulas much easier!

### 4. Smart File Browser with Auto-Copy ✅
- **Photo URL** and **Audio Note URL** now have intelligent file handling
- When you browse for a file:
  1. File is automatically copied to `assets/images/` or `assets/audio/`
  2. URL is set to GitHub Pages location
  3. Format: `https://aaroncelestian.github.io/specimenpro-events/assets/[type]/[filename]`
- Checks for existing files and asks before overwriting
- Creates directories automatically if they don't exist
- Shows success confirmation with file location

## New Directory Structure

```
specimenpro-events/
├── assets/
│   ├── images/          # Specimen photos
│   ├── audio/           # Audio notes
│   └── README.md        # Documentation
├── event_manager.py     # Enhanced GUI application
└── events.json          # Event data
```

## Usage Tips

### Working with Dates
1. Enter dates directly in the text field
2. Use any standard format (RFC, ISO, or YYYY-MM-DD)
3. Times should be in GMT (as required by the app)

### Adding Specimen Photos/Audio
1. Click "Browse" next to Photo URL or Audio Note URL
2. Select your file
3. File is automatically copied to the correct folder
4. URL is set to the GitHub Pages location
5. Commit and push the assets folder to make files available online

### Chemical Formulas
1. Type the base formula (e.g., "Ca Al Si O H O")
2. Click subscript/superscript buttons to add numbers
3. Example: Ca₂Al₃(Al,Si)₂Si₁₃O₃₆·12H₂O

## Technical Details

- Uses standard tkinter widgets (no external dependencies for UI)
- Uses `shutil.copy2` to preserve file metadata when copying files
- Automatically creates `assets/images/` and `assets/audio/` directories
- Accepts RFC 2822, ISO 8601, and simple YYYY-MM-DD date formats
- Unicode subscript/superscript characters for chemical formulas
