import os
import argparse
from io import BytesIO

from PIL import Image

import img2pdf


class WebpConverter:
    def __init__(self, input_path, output_path, quality):
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif')
        self.input_path = input_path
        self.output_path = output_path
        self.quality = quality
        self.method = 6  # Quality/speed trade-off (0=fast, 6=slower-better). Defaults to 4.

    # def __convert_image_file(self, file_name, input_file, output_file):
    #     try:
    #         with Image.open(input_file) as img:
    #             img.save(output_file, format='webp', quality=self.quality, method=self.method)
    #             print(f"Converted {file_name} to {output_file}")
    #     except Exception as e:
    #         print(f"Failed to convert {file_name}: {e}")
    #
    # def convert_to_webp(self):
    #     if not os.path.exists(self.output_path):
    #         os.makedirs(self.output_path)
    #
    #     for file_name in sorted(os.listdir(self.input_path)):
    #         if file_name.lower().endswith(self.supported_formats):
    #             input_file = os.path.join(self.input_path, file_name)
    #             output_file = os.path.join(self.output_path, f'{os.path.splitext(file_name)[0]}.webp')
    #             self.__convert_image_file(file_name, input_file, output_file)
    #
    # def convert_to_pdf(self):
    #     if not os.path.exists(self.output_path):
    #         os.makedirs(self.output_path)
    #
    #     webp_files = [file_name for file_name in os.listdir(self.output_path) if file_name.endswith('.webp')]
    #     webp_files.sort()
    #
    #     webp_images = []
    #     for file_name in webp_files:
    #         file_path = os.path.join(self.output_path, file_name)
    #         with Image.open(file_path) as img:
    #             if img.mode != 'RGBA':
    #                 img = img.convert('RGBA')
    #             webp_images.append(img)
    #
    #     if webp_images:
    #         output_pdf = os.path.join(self.output_path, 'out.pdf')
    #         webp_images[0].save(output_pdf, save_all=True, append_images=webp_images[1:], quality=self.quality)

    def __convert_image_buffer(self, file_name, input_file):
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
        buffers = []
        condition = lambda file_name: file_name.lower().endswith(self.supported_formats)
        file_list = list(filter(condition, os.listdir(self.input_path)))
        file_list.sort()
        for idx, file_name in enumerate(file_list):
            input_file = os.path.join(self.input_path, file_name)
            buffer = self.__convert_image_buffer(file_name, input_file)
            buffers.append(buffer)
            print(f"Processing {file_name} at {idx + 1}/{len(file_list)}")
        return buffers

    def convert_to_pdf(self, buffers):
        images = []
        for buffer in buffers:
            img = Image.open(buffer)
            images.append(img)

            # with Image.open(buffer) as img:
            # if img.mode != 'RGBA':
            #     img = img.convert('RGBA')
            # images.append(img)
            # output_pdf = os.path.join(self.output_path, 'output.pdf')
            # img.save(output_pdf, save_all=True, append_images=images[1:])
            # print(f"PDF created successfully with {len(images)} pages: {output_pdf}")

        output_pdf = os.path.join(self.output_path, 'output.pdf')
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
    parser.add_argument("-q", "--quality", type=int, default=85, help="Quality of WebP (default: 80)")
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
