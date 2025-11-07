# SpecimenPro Events

This repository contains the events page content and management tools for the [SpecimenPro iOS app](https://aaroncelestian.github.io/SpecimenPro-Webpage/).

## About

SpecimenPro is an iOS application for mineral specimen collectors and enthusiasts. This repository hosts the events data, web pages, and management tools for creating and managing SpecimenPro events.

## Structure

- `event_manager.py` - GUI application for managing events, specimens, and badges
- `events.json` - Event data file (created by the event manager)
- `index.html` - Events webpage displaying current events
- `about-events.html` - Information page about SpecimenPro events
- `specimenpro-style.css` - Shared stylesheet for web pages
- `requirements.txt` - Python dependencies for the event manager

## Event Manager GUI

The `event_manager.py` application provides a graphical interface for:
- Creating and managing events
- Adding specimen details with photos, audio notes, and metadata
- Defining achievement badges
- **Generating QR codes** for specimens using iOS deep links

### QR Code Generation

The event manager can generate QR codes for each specimen in an event. The QR codes use the iOS deep link format:

```
specimenpro://event/{eventId}/specimen/{specimenId}
```

**Two output formats available:**

1. **PNG Files** - Individual QR code image files
   - High error correction (ERROR_CORRECT_H) for damaged/dirty labels
   - Case-sensitive ID matching with JSON data
   - Descriptive filenames for easy identification
   - Batch generation for all specimens in an event

2. **PDF Grid** - Single PDF with QR codes arranged in a grid
   - Configurable grid layout (user-defined rows and columns)
   - Adjustable QR code size (0.5" to 3.0")
   - Page size options (Letter or A4)
   - Optional specimen names and IDs
   - Optional event title on first page
   - Multi-page support for large collections

### Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the event manager:
   ```bash
   python event_manager.py
   ```

3. Use the "Generate QR Codes ▼" dropdown button in the Specimens tab:
   - **Save as PNG Files** - Creates individual image files for each specimen
   - **Save as PDF Grid** - Creates a configurable PDF with QR codes in a grid layout

## Web Pages

- **Events Page** (`index.html`) - Displays current events with specimen and badge information
- **About Events** (`about-events.html`) - Information about how SpecimenPro events work

## Related Links

- [SpecimenPro Website](https://aaroncelestian.github.io/SpecimenPro-Webpage/)
- [Events Webpage](index.html)

## License

See [LICENSE](LICENSE) file for details.
