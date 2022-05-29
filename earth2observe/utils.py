import sys
import os
import gzip

def print_progress_bar(
        i: int,
        total: int,
        prefix: str="",
        suffix: str="",
        decimals: int=1,
        length: int=100,
        fill: str="█"
):
    """print_progress_bar.

    Parameters
    ----------
    i: [int]
        Iteration number
    total: [int]
        Total iterations
    prefix: [str]
        Name after bar
    suffix: [str]
        Decimals of percentage
    decimals: [int]

    length: [int]
        width of the waitbar
    fill: [str]
        bar fill
    """
    # Adjust when it is a linux computer
    if os.name == "posix" and total == 0:
        total = 0.0001

    percent = ("{0:." + str(decimals) + "f}").format(100 * (i / float(total)))
    filled = int(length * i // total)
    bar = fill * filled + "-" * (length - filled)

    sys.stdout.write("\r%s |%s| %s%% %s" % (prefix, bar, percent, suffix))
    sys.stdout.flush()

    if i == total:
        print()



def extractFromGZ(input_file, output_file, delete=False):
    """
    ExtractFromGZ method extract data from the zip/.gz files,
    save the data

    Parameters
    ----------
    input_file : [str]
        zipped file name .
    output_file : [str]
        directory where the unzipped data must be
                            stored.
    delete : [bool]
        True if you want to delete the zipped file after the extracting the data
    Returns
    -------
    None.
    """
    with gzip.GzipFile(input_file, "rb") as zf:
        content = zf.read()
        save_file_content = open(output_file, "wb")
        save_file_content.write(content)

    save_file_content.close()
    zf.close()

    if delete:
        os.remove(input_file)