import asyncio
import logging
import io
import os
from PIL import Image, ImageDraw, ImageFont  # type: ignore
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Try to import text shaping libraries for Arabic/Kurdish support
try:
    import arabic_reshaper  # type: ignore
    from bidi.algorithm import get_display  # type: ignore
    ARABIC_SUPPORT = True
    print("✓ Arabic/Kurdish text shaping libraries loaded successfully")
except ImportError:
    ARABIC_SUPPORT = False
    print(
        "⚠ Arabic/Kurdish text shaping libraries not found. Install with: pip install arabic-reshaper python-bidi"
    )

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "8171160278:AAFZIZ6tky8qrj5YGvZ1e-1HCAvCCW7U18k"  # Replace with your bot token"


class TextToImageBot:

    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Set up command and message handlers"""
        self.application.add_handler(
            CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND,
                           self.text_to_image))

    async def start_command(self, update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command"""
        welcome_message = ("بەم شێوە پڕی بکەرەوە\n"
                           "```\n"
                           "33 ABC 123\n"
                           "1500\n"
                           "1/5/2025 1 PM\n"
                           "ناوی تاجر\n"
                           "123456 SUL\n"
                           "ناوی سایق\n"
                           "```\n\n")
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def help_command(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command"""
        help_message = ("ℹ️ **How to use this bot:**\n\n"
                        "**Document Template Mode:**\n"
                        "Send exactly 6 lines for truck document:\n"
                        "Line 1: TR License Plate (e.g. `34 DN 7567`)\n"
                        "Line 2: Document Number (e.g. `1414`)\n"
                        "Line 3: Date & Time (e.g. `8/5/2025 1 PM`)\n"
                        "Line 4: Arabic Name (e.g. `احمدالعسافي`)\n"
                        "Line 5: IRQ License Plate (e.g. `17021 SUL`)\n"
                        "Line 6: Driver Name Arabic (e.g. `محمد خلف`)\n\n"
                        "**📝 Regular Text Mode:**\n"
                        "Send any other text for simple image conversion\n\n"
                        "**Commands:**\n"
                        "/start - Welcome message with example\n"
                        "/help - This help message\n\n"
                        "**Features:**\n"
                        "• Supports Arabic and English text\n"
                        "• Creates professional document templates\n"
                        "• Automatic font selection for Arabic\n"
                        "• High quality PNG output\n"
                        "• Works with both formats automatically")
        await update.message.reply_text(help_message, parse_mode='Markdown')

    def create_document_template(self) -> Image:
        """Load the template image or create a fallback"""
        try:
            # Try to load the user's uploaded template image
            template_paths = ["image.jpg", "template.png", "template.jpg"]

            for template_path in template_paths:
                if os.path.exists(template_path):
                    logger.info(f"Loading template: {template_path}")
                    img = Image.open(template_path)
                    # Convert to RGB if needed
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    return img

            logger.warning(
                "No template image found, creating fallback template")
            return self.create_fallback_template()

        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return self.create_fallback_template()

    def create_fallback_template(self) -> Image:
        """Create a fallback template if the user's image isn't available"""
        # Create base image (1280x720 - good size for documents)
        img = Image.new('RGB', (1280, 720), (240, 240, 240))
        draw = ImageDraw.Draw(img)

        # Draw document number box (top left - red border)
        draw.rectangle([50, 50, 300, 150],
                       fill=(255, 255, 255),
                       outline=(200, 50, 50),
                       width=4)

        # Draw TR license plate (top right - blue)
        draw.rectangle([900, 50, 1200, 120],
                       fill=(70, 130, 180),
                       outline=(0, 0, 0),
                       width=2)
        draw.text([910, 60],
                  "TR",
                  fill=(255, 255, 255),
                  font=self.get_font(60))

        # Draw name box (middle left - light blue)
        draw.rectangle([50, 200, 600, 280],
                       fill=(173, 216, 230),
                       outline=(100, 100, 100),
                       width=2)

        # Draw date/time box (middle right - light pink)
        draw.rectangle([650, 200, 1200, 280],
                       fill=(255, 182, 193),
                       outline=(100, 100, 100),
                       width=2)

        # Draw truck
        truck_y = 350
        # Truck cab (blue)
        draw.rectangle([50, truck_y, 200, truck_y + 150],
                       fill=(70, 130, 180),
                       outline=(0, 0, 0),
                       width=2)
        # Truck trailer (light gray)
        draw.rectangle([200, truck_y + 30, 700, truck_y + 120],
                       fill=(220, 220, 220),
                       outline=(0, 0, 0),
                       width=2)

        # IRQ license plate on truck (yellow)
        draw.rectangle([750, truck_y + 90, 1050, truck_y + 140],
                       fill=(255, 215, 0),
                       outline=(0, 0, 0),
                       width=2)
        draw.rectangle([750, truck_y + 90, 790, truck_y + 140],
                       fill=(255, 69, 0),
                       outline=(0, 0, 0),
                       width=1)
        draw.text([755, truck_y + 105],
                  "IRQ",
                  fill=(0, 0, 0),
                  font=self.get_font(20))
        draw.text([755, truck_y + 120],
                  "KR",
                  fill=(0, 0, 0),
                  font=self.get_font(18))

        return img

    def get_font(self, size: int, arabic: bool = False):
        """Get appropriate font for text rendering"""
        try:
            # Always try Kurdish font first for consistency
            fonts_to_try = []

            # Try multiple possible locations for Rabar_021.ttf
            kurdish_font_paths = [
                "Rabar_021.ttf", "./Rabar_021.ttf",
                os.path.join(os.getcwd(), "Rabar_021.ttf"),
                "fonts/Rabar_021.ttf", "./fonts/Rabar_021.ttf"
            ]

            # Add Kurdish font paths first
            fonts_to_try.extend(kurdish_font_paths)

            if arabic:
                # Add other Arabic-compatible fonts as fallbacks
                fonts_to_try.extend([
                    "arial.ttf", "ArialUni.ttf", "NotoSansArabic-Regular.ttf",
                    "Tahoma.ttf", "DejaVuSans.ttf"
                ])
            else:
                # Add other fonts for English text
                fonts_to_try.extend(["arial.ttf", "DejaVuSans.ttf"])

            # Try each font path
            for font_path in fonts_to_try:
                try:
                    font = ImageFont.truetype(font_path, size)
                    # Log successful font loading for debugging
                    if "Rabar" in font_path:
                        logger.info(
                            f"Successfully loaded Kurdish font: {font_path} (size: {size})"
                        )
                    return font
                except (OSError, IOError) as e:
                    # Only log Kurdish font loading issues for debugging
                    if "Rabar" in font_path:
                        logger.warning(
                            f"Could not load Kurdish font {font_path}: {e}")
                    continue

            logger.warning("No custom fonts found, using default font")
            return ImageFont.load_default()
        except Exception as e:
            logger.error(f"Error in font loading: {e}")
            return ImageFont.load_default()

    def is_arabic_text(self, text: str) -> bool:
        """Check if text contains Arabic/Kurdish characters"""
        # Check for Arabic and Kurdish Unicode ranges
        for char in text:
            code_point = ord(char)
            # Arabic block (U+0600-U+06FF)
            # Arabic Supplement (U+0750-U+077F)
            # Arabic Extended-A (U+08A0-U+08FF)
            # Arabic Presentation Forms-A (U+FB50-U+FDFF)
            # Arabic Presentation Forms-B (U+FE70-U+FEFF)
            if (0x0600 <= code_point <= 0x06FF
                    or 0x0750 <= code_point <= 0x077F
                    or 0x08A0 <= code_point <= 0x08FF
                    or 0xFB50 <= code_point <= 0xFDFF
                    or 0xFE70 <= code_point <= 0xFEFF):
                return True
        return False

    def shape_kurdish_text(self, text: str) -> str:
        """Properly shape Kurdish/Arabic text for display"""
        try:
            if not self.is_arabic_text(text):
                return text

            if ARABIC_SUPPORT:
                # Create a reshaper with Kurdish-friendly configuration
                reshaper = arabic_reshaper.ArabicReshaper(
                    configuration={
                        'delete_harakat': False,  # Keep diacritics
                        'support_zwj': True,  # Support zero-width joiner
                        'shift_harakat_position': False,
                        'support_tatweel': True,  # Support tatweel (kashida)
                        'use_unshaped_instead_of_isolated': False,
                    })

                # Reshape the text to connect letters properly
                reshaped_text = reshaper.reshape(text)

                # Apply bidirectional algorithm for proper display
                display_text = get_display(reshaped_text)

                logger.info(
                    f"Shaped Kurdish text: '{text}' -> '{display_text}'")
                return display_text
            else:
                logger.warning(
                    "Arabic reshaping not available, text may not display correctly"
                )
                return text

        except Exception as e:
            logger.error(f"Error shaping Kurdish text: {e}")
            return text

    def parse_document_input(self, text: str) -> dict:
        """Parse the structured input format"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        if len(lines) != 6:
            return None

        return {
            'tr_plate': lines[0],  # 34 DN 7567
            'doc_number': lines[1],  # 1414
            'datetime': lines[2],  # 8/5/2025 1 PM
            'arabic_name': lines[3],  # احمدالعسافي
            'irq_plate': lines[4],  # 17021 SUL
            'driver_name': lines[5]  # محمد خلف
        }

    def create_document_image(self, text: str) -> io.BytesIO:
        """Create document image with structured input"""
        try:
            # Parse input
            data = self.parse_document_input(text)
            if not data:
                raise ValueError("Invalid input format")

            # Create base template
            img = self.create_document_template()
            draw = ImageDraw.Draw(img)

            # Get image dimensions for positioning
            img_width, img_height = img.size

            # Scale factors based on image size (assuming template is proportional)
            scale_x = img_width / 1280
            scale_y = img_height / 720

            # Add document number (top left red-bordered box)
            font_large = self.get_font(int(
                120 *
                min(scale_x, scale_y)))  # Adjusted to match reference image
            bbox = draw.textbbox((0, 0), data['doc_number'], font=font_large)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            # Center in the red-bordered box
            x = int((img_width * 0.215) -
                    (text_width // 2))  # Left side box center
            y = int(
                (img_height * 0.10) - (text_height // 2))  # Top area center
            draw.text((x, y),
                      data['doc_number'],
                      fill=(0, 0, 0),
                      font=font_large)

            # Add TR license plate number (top right blue plate - white area)
            font_plate = self.get_font(int(
                88 *
                min(scale_x, scale_y)))  # Adjusted to match reference image
            bbox = draw.textbbox((0, 0), data['tr_plate'], font=font_plate)
            text_width = bbox[2] - bbox[0]
            # Position in the white area of the TR plate
            x = int((img_width * 0.75) -
                    (text_width // 2))  # Right side white area
            y = int(img_height * 0.08)  # Top area - moved higher up
            draw.text((x, y),
                      data['tr_plate'],
                      fill=(0, 0, 0),
                      font=font_plate)

            # Add Arabic name (middle left - light blue box)
            font_arabic = self.get_font(
                int(85 * min(scale_x, scale_y)),
                arabic=True)  # Adjusted to match reference image
            shaped_arabic_name = self.shape_kurdish_text(data['arabic_name'])
            bbox = draw.textbbox((0, 0), shaped_arabic_name, font=font_arabic)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            # Center in the light blue box
            x = int((img_width * 0.26) -
                    (text_width // 2))  # Left side blue box center
            y = int((img_height * 0.44) - (text_height // 2))  # Middle area
            draw.text((x, y),
                      shaped_arabic_name,
                      fill=(0, 0, 0),
                      font=font_arabic)

            # Add date/time (middle right - pink box)
            font_date = self.get_font(int(
                72 *
                min(scale_x, scale_y)))  # Adjusted to match reference image
            bbox = draw.textbbox((0, 0), data['datetime'], font=font_date)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            # Center in the pink box
            x = int((img_width * 0.75) -
                    (text_width // 2))  # Right side pink box center
            y = int((img_height * 0.45) - (text_height // 2))  # Middle area
            draw.text((x, y), data['datetime'], fill=(0, 0, 0), font=font_date)

            # Add IRQ plate number (bottom right yellow plate - white area)
            font_irq = self.get_font(int(
                74 *
                min(scale_x, scale_y)))  # Adjusted to match reference image
            bbox = draw.textbbox((0, 0), data['irq_plate'], font=font_irq)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            # Position in the white area of the IRQ plate
            x = int((img_width * 0.78) -
                    (text_width // 2))  # Right side white area
            y = int((img_height * 0.77) -
                    (text_height // 2))  # Bottom yellow plate area
            draw.text((x, y), data['irq_plate'], fill=(0, 0, 0), font=font_irq)

            # Add driver name on truck trailer (Arabic text)
            font_driver = self.get_font(
                int(80 * min(scale_x, scale_y)),
                arabic=True)  # Adjusted to match reference image
            shaped_driver_name = self.shape_kurdish_text(data['driver_name'])
            bbox = draw.textbbox((0, 0), shaped_driver_name, font=font_driver)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            # Position on the gray trailer area
            x = int(
                (img_width * 0.32) - (text_width // 2))  # Center of trailer
            y = int(
                (img_height * 0.74) - (text_height // 2))  # On trailer level
            draw.text((x, y),
                      shaped_driver_name,
                      fill=(0, 0, 0),
                      font=font_driver)

            # Save to BytesIO
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            return img_bytes

        except Exception as e:
            logger.error(f"Error creating document image: {e}")
            raise

    def create_text_image(self,
                          text: str,
                          max_width: int = 800,
                          font_size: int = 70) -> io.BytesIO:
        """Convert text to PNG image - supports both document format and regular text"""
        try:
            # Check if input matches document format (6 lines)
            lines = [line.strip() for line in text.split('\n') if line.strip()]

            if len(lines) == 6:
                # This looks like document input, create document image
                return self.create_document_image(text)

            # Fall back to regular text image
            # Try to use a nice font, fallback to default if not available
            font = self.get_font(font_size, self.is_arabic_text(text))

            # Create a temporary image to measure text
            temp_img = Image.new('RGBA', (1, 1), (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_img)

            # Word wrapping
            words = text.split()
            lines = []
            current_line = []

            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = temp_draw.textbbox((0, 0), test_line, font=font)
                line_width = bbox[2] - bbox[0]

                if line_width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        # Single word is too long, add it anyway
                        lines.append(word)

            if current_line:
                lines.append(' '.join(current_line))

            # Calculate image dimensions
            line_height = font_size + 10
            padding = 40

            # Get the maximum line width
            max_line_width = 0
            for line in lines:
                bbox = temp_draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                max_line_width = max(max_line_width, line_width)

            img_width = max_line_width + (padding * 2)
            img_height = (len(lines) * line_height) + (padding * 2)

            # Create the actual image with transparent background
            img = Image.new('RGBA', (img_width, img_height),
                            (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)

            # Draw text
            y_offset = padding
            for line in lines:
                # Shape Kurdish/Arabic text if needed
                shaped_line = self.shape_kurdish_text(line)

                # Center the text horizontally
                bbox = draw.textbbox((0, 0), shaped_line, font=font)
                line_width = bbox[2] - bbox[0]
                x_offset = (img_width - line_width) // 2

                # Draw text with black color
                draw.text((x_offset, y_offset),
                          shaped_line,
                          font=font,
                          fill=(0, 0, 0, 255))
                y_offset += line_height

            # Save to BytesIO
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            return img_bytes

        except Exception as e:
            logger.error(f"Error creating image: {e}")
            raise

    async def text_to_image(self, update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages and convert them to images"""
        try:
            user_text = update.message.text

            # Check text length
            if len(user_text) > 500:
                await update.message.reply_text(
                    "⚠️ Text is too long! Please keep it under 500 characters for best results."
                )
                return

            # Show typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action="upload_photo")

            # Create image
            img_bytes = self.create_text_image(user_text)

            # Send image
            await update.message.reply_photo(
                photo=img_bytes,
                caption=
                f"وەسڵی بار\n\n📝 {user_text[:50]}{'...' if len(user_text) > 50 else ''}"
            )

            logger.info(
                f"Generated image for user {update.effective_user.id}: {user_text[:50]}..."
            )

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(
                "❌ Sorry, I couldn't create an image from your text. Please try again!"
            )

    async def error_handler(self, update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")

    def run(self):
        """Start the bot"""
        logger.info("Starting Text to Image Bot...")

        # Add error handler
        self.application.add_error_handler(self.error_handler)

        # Start the bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = TextToImageBot()
    bot.run()
