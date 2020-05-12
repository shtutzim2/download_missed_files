import argparse
import pathlib
import urllib.request
from functools import partial
from multiprocessing import Pool, cpu_count

from utils.main_logger import logger

# Argument parser.
parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, help="File that contain file names to download.")
parser.add_argument("--output", type=str, default="../output", help="Folder to save all downloads.")

args = parser.parse_args()


def get_url_from_path(file_to_download):
    if file_to_download[-1] == "\n":
        file_to_download = file_to_download[:-1]
    path = file_to_download

    if path.startswith("mirror"):
        path = path.split("/", 1)[1]
    else:
        # Todo : Check which path can be here and add support to them.
        raise Exception(f"Not handle this path, path is : {path}")

    return f"http://{path}"


def download_file(url, output_dir):
    try:
        url_path = url[len("http://"):]

        # url might look like:
        # http://ftp.us.debian.org/debian/pool/main/libd/libdigest-elf-perl/libdigest-elf-perl_1.42-1+b4_amd64.deb
        # and for get only the dir we split it from the end by '\' and take the first part.
        folder_path_in_url = url_path.rsplit("/", 1)[0]

        output_dir_path = pathlib.Path(output_dir / folder_path_in_url)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        urllib.request.urlretrieve(url=url, filename=str(output_dir / url_path))
        logger.info(f"Download file : {url}")
    except Exception as e:
        logger.exception(e)


def main():
    file_with_names_of_files_to_download = pathlib.Path(args.input)
    output_folder = pathlib.Path(args.output)
    output_folder.mkdir(parents=True, exist_ok=True)

    files_to_download = list()

    with open(file_with_names_of_files_to_download, 'r') as f:
        for line in f:
            url_path_to_download = get_url_from_path(line)
            files_to_download.append(url_path_to_download)

    logger.info(f"Start downloading, using {cpu_count()} threads.")
    pool = Pool(cpu_count())
    download_func = partial(download_file, output_dir=output_folder)
    pool.map(download_func, files_to_download)
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
