from PIL import Image, ImageDraw


class ImageCorrector:
    def __init__(self, pillow_img: Image, setting: dict[str, str]) -> None:
        self.pillow_img = pillow_img
        self.setting = setting

    def correct(self) -> Image:
        figure = self.setting.get("FIGURE")

        if figure == "ROUNDED RECTANGLE":
            self.create_rounded_square(pillow_img=self.pillow_img)
        elif figure == "ROUNDED DIAMOND":
            self.create_rounded_diamond(pillow_img=self.pillow_img)

        return self.pillow_img

    def create_rounded_square(self, pillow_img: Image, radius: int = 50) -> Image:
        # Задайте размер изображения и радиус скругления углов
        width, height = pillow_img.size
        border_radius = radius

        # Создайте изображение и контекст рисования
        img = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(img)

        # Нарисуйте прямоугольник с скругленными углами
        draw.rectangle([(border_radius, 0), (width - border_radius, height)], fill=255)
        draw.rectangle([(0, border_radius), (width, height - border_radius)], fill=255)
        draw.ellipse((0, 0, border_radius * 2, border_radius * 2), fill=255)
        draw.ellipse(
            (0, height - border_radius * 2, border_radius * 2, height), fill=255
        )
        draw.ellipse((width - border_radius * 2, 0, width, border_radius * 2), fill=255)
        draw.ellipse(
            (width - border_radius * 2, height - border_radius * 2, width, height),
            fill=255,
        )

        result = Image.new("RGBA", pillow_img.size)
        result.paste(pillow_img, (0, 0), img)
        self.pillow_img = result

        return result

    def create_rounded_diamond(self, pillow_img: Image, radius: int = 100) -> Image:
        # Задайте размер изображения и радиус скругления углов
        width, height = pillow_img.size
        border_radius = radius * 2

        # Создайте изображение и контекст рисования
        img = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(img)

        w = width / 8
        h = height / 8

        draw.rectangle(
            [(border_radius, h), (width - border_radius, height - h)], fill=255
        )
        draw.rectangle(
            [(w, border_radius), (width - w, height - border_radius)], fill=255
        )

        draw.ellipse((w, h, border_radius * 2 - w, border_radius * 2 - h), fill=255)
        draw.ellipse(
            (w, height - border_radius * 2 + h, border_radius * 2 - w, height - h),
            fill=255,
        )
        draw.ellipse(
            (w + width - border_radius * 2, h, width - w, border_radius * 2 - h),
            fill=255,
        )
        draw.ellipse(
            (
                w + width - border_radius * 2,
                h + height - border_radius * 2,
                width - w,
                height - h,
            ),
            fill=255,
        )
        img = img.rotate(45)

        result = Image.new("RGBA", pillow_img.size)
        result.paste(pillow_img, (0, 0), img)
        self.pillow_img = result

        return result
