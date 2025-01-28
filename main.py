import argparse
import os
from io import BytesIO
from multiprocessing import Pool, cpu_count

from PIL import Image, ImageEnhance, ImageFilter


class PDFConverter:
    def __init__(self, args):
        self.anomaly_detected_size = False
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif')
        self.input_path = args.input_path
        self.output_path = args.output_path if args.output_path else os.path.join(args.input_path, 'out')
        self.quality = args.quality
        self.resize_ratio = args.resize_ratio
        self.method = 6  # Quality/speed trade-off (0=fast, 6=slower-better). Defaults to 4.
        self.crop_ratio = 0.015
        self.contrast = 1.1
        self.max_width = 0
        self.max_height = 0

    def check_image_size(self, input_file):
        with Image.open(input_file) as image:
            image = self.__crop_image(image)
            width, height = image.size
            return width, height

    def __crop_image(self, image):
        width, height = image.size
        left = width * self.crop_ratio
        top = height * self.crop_ratio
        right = width - left
        bottom = height - top
        return image.crop((left, top, right, bottom))

    def __enhance_image(self, image):
        image = ImageEnhance.Contrast(image).enhance(self.contrast)
        image = image.filter(ImageFilter.MedianFilter(size=3))
        return image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

    def __add_border(self, image):
        width, height = image.size
        if (self.max_width / width > 1.1) or (self.max_height / height > 1.1):
            self.anomaly_detected_size = True
        # print(f'current image size ratio: {round(self.max_width / width, 3)}, {round(self.max_height / height, 3)}')
        left = (self.max_width - width) // 2
        top = (self.max_height - height) // 2
        new_image = Image.new('RGB', (self.max_width, self.max_height), (255, 255, 255))
        new_image.paste(image, (left, top))
        return new_image

    def __resize_image(self, image):
        cur_width, cur_height = image.size
        width = int(cur_width * self.resize_ratio)
        height = int(cur_height * self.resize_ratio)
        return image.resize((width, height), Image.Resampling.LANCZOS)

    def __save_image(self, image, image_file):
        file_name = image_file + '.jpg'
        image_path = os.path.join(self.output_path, file_name)
        image.save(image_path,
                   format='JPEG',
                   quality=self.quality,
                   progressive=True)

    def convert_image(self, file_path):
        print(f"Processing {file_path}")
        temp_image = BytesIO()
        try:
            with Image.open(file_path) as image:
                image = self.__crop_image(image)
                image = self.__enhance_image(image)
                image = self.__add_border(image)
                image = self.__resize_image(image)
                image.save(temp_image,
                           format='JPEG',
                           quality=self.quality,
                           progressive=True)
        except Exception as e:
            print(f"Failed to convert {file_path}: {e}")
        return temp_image

    def __convert_to_jpg(self):
        images = []
        condition = lambda file_name: file_name.lower().endswith(self.supported_formats)
        file_list = list(filter(condition, os.listdir(self.input_path)))
        file_list.sort()

        pool_size = cpu_count()
        with Pool(pool_size) as pool:
            file_paths = map(lambda _file_name: os.path.join(self.input_path, _file_name), file_list)
            async_result = pool.map_async(self.check_image_size, file_paths)
            results = async_result.get()
            widths, heights = zip(*results)
            self.max_width = max(widths)
            self.max_height = max(heights)
        with Pool(pool_size) as pool:
            file_paths = map(lambda _file_name: os.path.join(self.input_path, _file_name), file_list)
            async_result = pool.map_async(self.convert_image, file_paths)
            results = async_result.get()
            images.extend(results)
        return images

    def __convert_to_pdf(self, temp_images):
        output_pdf = os.path.join(self.output_path, 'output.pdf')
        images = []
        for temp_image in temp_images:
            img = Image.open(temp_image)
            images.append(img)
        if images:
            try:
                print(f"creating PDF file... {len(images)} pages: {output_pdf}")
                images[0].save(output_pdf, save_all=True, append_images=images[1:])
                print(f"PDF created successfully with {len(images)} pages: {output_pdf}")
            except Exception as e:
                print(f"Failed to convert {output_pdf}: {e}")
                print(e.__traceback__)
        for img in images:
            img.close()

    def __check_anomaly(self):
        if self.anomaly_detected_size:
            print("Anomaly Detected: size anomaly")

    def convert(self):
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        jpg_images = self.__convert_to_jpg()
        self.__convert_to_pdf(jpg_images)
        self.__check_anomaly()


def main():
    parser = argparse.ArgumentParser(description="Convert images to pdf file.")
    parser.add_argument("input_path", type=str, help="Input file or directory")
    parser.add_argument("-o", "--output_path", type=str, help="Output directory")
    parser.add_argument("-q", "--quality", type=int, default=85, help="Quality of image (default: 85)")
    parser.add_argument("-r", "--resize_ratio", type=int, default=0.5,
                        help="Resizes the image by multiplying its dimensions with the specified scale factor")
    args = parser.parse_args()

    converter = PDFConverter(args)
    converter.convert()


if __name__ == "__main__":
    main()
