import os
import subprocess


def convert_pptx_to_pdf(file: str, output: str) -> str:
    output_dir = os.path.dirname(output)
    cmd = f"libreoffice --headless --convert-to pdf --outdir {output_dir} {file}"
    subprocess.run(cmd, shell=True)
    return output


def convert_pdf_to_pptx(file: str, save_path: str) -> str:
    output_dir = os.path.dirname(save_path)
    cmd = f"libreoffice --headless --infilter='impress_pdf_import' --convert-to pptx --outdir {output_dir} {file}"   # noqa E501
    subprocess.run(cmd, shell=True)
    return save_path
