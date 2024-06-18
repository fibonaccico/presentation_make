from make_presentation.templates import USUAL_PICTURES


def get_pictures_sizes(template_name: str, number_of_slides: int) -> list[list[str]]:
    """
    Return a list of pictures sizes list for each slide according to
    a template of presentation we use.
    """

    pictures: list[list[str]] = []

    setting = USUAL_PICTURES[template_name]

    for i in range(number_of_slides):
        usual_slide_set = setting[i % len(setting)]

        pictures_in_one_slide = []
        if usual_slide_set:
            for picture in usual_slide_set:
                pictures_in_one_slide.append((picture["SIZE"]))

        pictures.append(pictures_in_one_slide)

    return pictures
