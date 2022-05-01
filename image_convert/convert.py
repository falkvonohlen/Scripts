import os
from pathlib import Path
from sys import prefix
from PIL import Image

dir = os.path.dirname(__file__)
in_dir = os.path.join(dir, "input")
out_dir = os.path.join(dir, "output")

quality = 90
widths = [512,1024,2048,-1]
prefix = "img"


def resize_image(img: Image.Image, width: int) -> Image.Image:
    wpercent = (width/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    return img.resize((width, hsize), Image.LANCZOS)


def save_webp_image(img: Image.Image, path: str, quality: int) -> None:
    img.save(path, 'webp', optimize=True, quality=quality)


def create_html_picture_tag(prefix: str, image_range: list[str], copy_image: str, out_folder: str) -> None:
    tag = "<picture>\n"
    for image_name in image_range:
        file_name = image_name.replace(out_folder, "")
        path = f"{prefix}{file_name}".replace('\\', '/')
        tag += f"\t<source srcset='{path}' type='image/webp' media='(min-width:0px)'/>\n"

    file_name = copy_image.replace(out_folder, "")
    path = f"{prefix}{file_name}".replace('\\', '/')
    tag += f"\t<img src='{path}' alt='...' loading='lazy' />\n"

    tag += "</picture>"

    with open(os.path.join(out_folder, "picture_tag.html"), 'w') as out_stream:
        out_stream.write(tag)


def creat_image_range(img: Image.Image, out_folder: str, image_name: str, quality: int) -> list[str]:
    # The widths in which the image will be saved. -1 for original size
    # Example: widths = [128, 256, 512, 1024, -1]
    images = []
    for width in widths:
        if width == -1:
            out_path = f"{out_folder}/{image_name}.webp"
            out_img = img
        else:
            out_path = f"{out_folder}/{image_name}_{width}.webp"
            out_img = resize_image(img, width)

        images.append(out_path)
        save_webp_image(out_img, out_path, quality)

    return images


def load_image(path) -> None:
    return Image.open(path)


def create_webp_images_for_website():
    for root, dirs, files in os.walk(in_dir):
        for file in files:
            image_paths = []
            path = Path(os.path.join(root, file))
            image_dir = Path(os.path.join(out_dir, path.stem))
            image_dir.mkdir(exist_ok=True)
            image_dir = image_dir.resolve().__str__()
            with Image.open(path) as img:
                # Copy the original image
                copy_path = os.path.join(image_dir, path.name)
                img.save(copy_path)
                # Create webp size range
                for p in creat_image_range(img, image_dir, path.stem, quality):
                    image_paths.append(p)

            create_html_picture_tag(prefix, image_paths, copy_path, image_dir)


if __name__ == "__main__":
    create_webp_images_for_website()
