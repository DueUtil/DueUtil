import os
import re
import asyncio

from PIL import Image
from ... import dbconn, util

# Imaged used in more than 1 quest or weapon
repeated_usages = dict()

async def cache_image(url):
    filename = get_cached_filename(url)
    if os.path.isfile(filename):
        # Already used somewhere
        if filename in repeated_usages:
            repeated_usages[filename] += 1
        else:
            repeated_usages[filename] = 2
    else:
        try:
            image_data = await util.download_file(url)
            image = Image.open(image_data)
            # cache image
            image.convert('RGB').save(filename, optimize=True, quality=20)
            return image
        except:
            # We don't care what went wrong
            if os.path.isfile(filename):
                os.remove(filename)
            return None


def uncache_if_unreferenced(url):
    filename = get_cached_filename(url)
    if filename in repeated_usages:
        repeated_usages[url] -= 1
        if repeated_usages[url] == 1:
            del repeated_usages[url]
    else:
        uncache(url)


def uncache(url):
    try:
        os.remove(get_cached_filename(url))
        util.logger.info("Removed %s from image cache (no longer needed)" % url)
    except IOError as exception:
        util.logger.warning("Failed to delete cached image %s (%s)" % (url, exception))


def get_cached_filename(name):
    filename = 'assets/imagecache/' + re.sub(r'\W+', '', name)
    if len(filename) > 128:
        filename = filename[:128]
    return filename + '.jpg'

