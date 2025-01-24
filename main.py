import argparse
import os
from io import BytesIO

from PIL import Image


class WebpConverter:
    def __init__(self, input_path, output_path, quality):
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif')
        self.input_path = input_path
        self.output_path = output_path
        self.quality = quality
        self.method = 6  # Quality/speed trade-off (0=fast, 6=slower-better). Defaults to 4.

    def __convert_image(self, file_name, input_file):
        buffer = BytesIO()
        try:
            with Image.open(input_file) as img:
                img.save(buffer,
                         format='JPEG',
                         quality=self.quality,
                         progressive=True)
        except Exception as e:
            print(f"Failed to convert {file_name}: {e}")
        return buffer

    def convert_to_jpg(self):
        converted_images = []
        condition = lambda file_name: file_name.lower().endswith(self.supported_formats)
        file_list = list(filter(condition, os.listdir(self.input_path)))
        file_list.sort()
        for idx, file_name in enumerate(file_list):
            input_file = os.path.join(self.input_path, file_name)
            buffer = self.__convert_image(file_name, input_file)
            converted_images.append(buffer)
            print(f"Processing {file_name} at {idx + 1}/{len(file_list)}")
        return converted_images

    def convert_to_pdf(self, buffers):
        output_pdf = os.path.join(self.output_path, 'output.pdf')
        images = []
        for buffer in buffers:
            img = Image.open(buffer)
            images.append(img)
        try:
            images[0].save(output_pdf, save_all=True, append_images=images[1:])
            print(f"PDF created successfully with {len(images)} pages: {output_pdf}")
        except Exception as e:
            print(f"Failed to convert {output_pdf}: {e}")
            print(e.__traceback__)
        for img in images:
            img.close()

    def convert(self):
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        buffers = self.convert_to_jpg()
        self.convert_to_pdf(buffers)


def main():
    parser = argparse.ArgumentParser(description="Convert images to WebP format.")
    parser.add_argument("input_path", type=str, help="Input file or directory")
    parser.add_argument("-o", "--output_path", type=str, help="Output directory")
    parser.add_argument("-q", "--quality", type=int, default=85, help="Quality of WebP (default: 85)")
    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path if args.output_path else os.path.join(input_path, 'out')
    quality = args.quality

    converter = WebpConverter(input_path, output_path, quality)
    # converter.convert_to_webp()
    # converter.convert_to_pdf()
    converter.convert()


if __name__ == "__main__":
    main()
