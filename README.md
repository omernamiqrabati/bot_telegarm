# Telegram Text to Image Bot 🎨

A Telegram bot that converts text messages into beautiful PNG images with transparent backgrounds.

## Features

- 🎨 Convert any text message to a PNG image
- 📝 Automatic text wrapping for long messages
- 🔤 Clean, readable fonts with fallback options
- 🌟 Transparent background for versatile use
- 📏 Optimized image dimensions
- ⚡ Fast and responsive

## Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the bot:
   ```bash
   python main.py
   ```

## Usage

### Commands

- `/start` - Welcome message and introduction
- `/help` - Show help and usage instructions

### Basic Usage

1. Start a chat with your bot on Telegram
2. Send any text message (up to 500 characters)
3. The bot will convert your text to a PNG image and send it back
4. Download and use your image!

## Bot Features

### Text Processing
- Automatic word wrapping to fit image width
- Centered text alignment
- Optimized font size and spacing
- Support for multiple lines

### Image Generation
- High-quality PNG output
- Transparent background
- Automatic image sizing based on text content
- Black text on transparent background for maximum compatibility

### Error Handling
- Graceful handling of long text (500+ characters)
- Font fallback system (Arial → DejaVu Sans → Default)
- Comprehensive error logging
- User-friendly error messages

## Technical Details

### Dependencies
- `python-telegram-bot` - Telegram Bot API wrapper
- `Pillow` - Python Imaging Library for image generation

### Image Specifications
- Format: PNG with transparency
- Font: Arial (with fallbacks)
- Font size: 32px
- Max width: 800px
- Padding: 40px
- Line spacing: 42px (font size + 10px)

## Customization

You can modify the following parameters in the code:

- `max_width`: Maximum image width (default: 800px)
- `font_size`: Text font size (default: 32px)  
- `padding`: Image padding (default: 40px)
- `line_height`: Space between lines (default: font_size + 10px)

## Bot Token

The bot is configured with the token: `7254600037:AAG2630rLOEzzAa5lDtBlP2kfkqFvdcOIOI`

⚠️ **Note**: In production, store your bot token securely using environment variables instead of hardcoding it.

## Logging

The bot includes comprehensive logging that tracks:
- Bot startup and shutdown
- User interactions
- Image generation events
- Error occurrences

## Error Handling

The bot handles various error scenarios:
- Text too long (>500 characters)
- Font loading failures
- Image generation errors
- Network connectivity issues

## Support

If you encounter any issues:
1. Check the console output for error messages
2. Ensure all dependencies are installed correctly
3. Verify your internet connection for Telegram API access
4. Check that the bot token is valid and active

## License

This project is open source and available under the MIT License. 