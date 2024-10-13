from PIL import Image, ImageDraw, ImageFont


def add_text_to_image(image_path:str, text:str, output_path:str, position:tuple=(20, 100), font_size:int=15, font_type:str|None = None, font_color:str|None = None) -> str:
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    padding = 10

    if font_size == 15:
        font_size = int(image.height * 0.05)


    if font_type is None:
        font_type = "arial.ttf"

    font = ImageFont.truetype(font_type, font_size)

    if font_color is None:
        font_color = 'black'


    max_width = image.width - 2 * padding
    paragraphs = text.split('\n')
    lines = []
    #words = text.split(' ')
    current_line = ' '

    for paragraph in paragraphs:
        words = paragraph.split()

        for word in words:
            # Check if adding the next word exceeds the max width
            test_line = current_line + ((word + ' ') if current_line else word)

            if draw.textlength(test_line, font=font) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + ' '  # Start a new line with the current word

        if current_line:  # Add any remaining text
            lines.append(current_line)
            current_line = '  '

    # Calculate vertical positioning for the first line
    y = position[1]

    # Draw each line on the image
    for line in lines:
        draw.text((position[0], y), line, font=font, fill=font_color)
        y += font.size + padding  # Move y down for the next line


    # Save the edited image
    image.save(output_path)

    return output_path
