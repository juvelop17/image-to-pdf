import argparse
import os
from io import BytesIO
from multiprocessing import Pool, cpu_count

import tqdm
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

    def check_image_size(self, file_path):
        with Image.open(file_path) as image:
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

    def __check_images(self, input_path, file_list):
        print(f"Checking {len(file_list)} images...")
        widths = []
        heights = []
        pool_size = cpu_count()
        file_paths = list(map(lambda file_name: os.path.join(input_path, file_name), file_list))
        with Pool(pool_size) as pool:
            results = pool.imap(self.check_image_size, file_paths)
            for result in tqdm.tqdm(results, total=len(file_paths)):
                widths.append(result[0]), heights.append(result[1])
        if widths:
            self.max_width = max(widths)
        if heights:
            self.max_height = max(heights)
        return file_paths, pool_size

    def __convert_images(self, input_path, file_list):
        print(f"Processing {len(file_list)} images...")
        images = []
        pool_size = cpu_count()
        file_paths = list(map(lambda file_name: os.path.join(input_path, file_name), file_list))
        with Pool(pool_size) as pool:
            results = pool.imap(self.convert_image, file_paths)
            for result in tqdm.tqdm(results, total=len(file_paths)):
                images.append(result)
        return images

    def __extension_filter(self, file_name):
        return file_name.lower().endswith(self.supported_formats)

    def __convert_to_jpg(self, input_path):
        file_list = list(filter(self.__extension_filter, os.listdir(input_path)))
        file_list.sort()
        self.__check_images(input_path, file_list)
        return self.__convert_images(input_path, file_list)

    def __convert_to_pdf(self, temp_images, output_name):
        output_pdf = os.path.join(self.output_path, f'{output_name}.pdf')
        images = []
        for temp_image in temp_images:
            img = Image.open(temp_image)
            images.append(img)
        if images:
            try:
                print(f"Creating PDF file... {len(images)} pages: {output_pdf}")
                images[0].save(output_pdf, save_all=True, append_images=images[1:])
                print(f"PDF created successfully with {len(images)} pages: {output_pdf}")
            except Exception as e:
                print(f"Failed to convert {output_pdf}: {e}")
                print(e.__traceback__)
        for img in images:
            img.close()

    def __check_anomaly(self, input_path):
        if self.anomaly_detected_size:
            print(f"Anomaly Detected: size anomaly. {input_path}")
            self.anomaly_detected_size = False

    def __process(self, input_path):
        output_name = os.path.basename(input_path)
        jpg_images = self.__convert_to_jpg(input_path)
        self.__convert_to_pdf(jpg_images, output_name)
        self.__check_anomaly(input_path)

    def convert(self):
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        directory = [os.path.abspath(self.input_path)]
        for entry in os.listdir(self.input_path):
            path = os.path.join(self.input_path, entry)
            if os.path.isdir(path):
                directory.append(path)
        for d in directory:
            print(f"Begin converting... {d}")
            self.__process(d)


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
