import argparse
import os
from io import BytesIO

from PIL import Image


class WebpConverter:
    def __init__(self, args):
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif')
        self.input_path = args.input_path
        self.output_path = args.output_path if args.output_path else os.path.join(args.input_path, 'out')
        self.quality = args.quality
        self.dpi = args.dpi
        self.method = 6  # Quality/speed trade-off (0=fast, 6=slower-better). Defaults to 4.

    def __convert_image(self, file_name, input_file):
        temp_file_name = file_name.split('.')[0] + '.jpg'
        temp_image = os.path.join(self.output_path, temp_file_name)
        try:
            with Image.open(input_file) as image:
                resized_image = self.__resize_image(image)
                resized_image.save(temp_image,
                         format='JPEG',
                         quality=self.quality,
                         dpi=(self.dpi, self.dpi),
                         progressive=True)
        except Exception as e:
            print(f"Failed to convert {file_name}: {e}")
        return temp_image

    def __resize_image(self, image):
        original_dpi = image.info.get("dpi", None)
        if original_dpi is None:
            return image

        x_dpi, y_dpi = original_dpi
        ratio = self.dpi / x_dpi
        cur_width, cur_height = image.size
        width = int(cur_width * ratio)
        height = int(cur_height * ratio)
        return image.resize((width, height), Image.Resampling.LANCZOS)

    def convert_to_jpg(self):
        converted_images = []
        condition = lambda file_name: file_name.lower().endswith(self.supported_formats)
        file_list = list(filter(condition, os.listdir(self.input_path)))
        file_list.sort()
        for idx, file_name in enumerate(file_list):
            input_file = os.path.join(self.input_path, file_name)
            temp_image = self.__convert_image(file_name, input_file)
            converted_images.append(temp_image)
            print(f"Processing {file_name} at {idx + 1}/{len(file_list)}")
        return converted_images

    def convert_to_pdf(self, temp_images):
        output_pdf = os.path.join(self.output_path, 'output.pdf')
        images = []
        for temp_image in temp_images:
            img = Image.open(temp_image)
            images.append(img)
        if images:
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
    parser.add_argument("-q", "--quality", type=int, default=85, help="Quality of image (default: 85)")
    parser.add_argument("-d", "--dpi", type=int, default=300, help="DPI of image (default: 300)")
    args = parser.parse_args()

    converter = WebpConverter(args)
    converter.convert()


if __name__ == "__main__":
    main()
