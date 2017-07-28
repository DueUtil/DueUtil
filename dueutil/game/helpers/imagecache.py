import os
import re
import json
from PIL import Image
from ... import dbconn, util, tasks
import traceback


class _CacheStats:
    # Simple holder class (to work with dbconn)
    # (since it's easier than getting a namedturple to serialize)
    def __init__(self):
        self.repeated_usages = dict()

stats = _CacheStats()
# Imaged used in more than 1 quest or weapon
repeated_usages = stats.repeated_usages


def image_used(url):
    # Called when an image is first used.
    # Keeps track of images that are used > 1 times
    if os.path.isfile(get_cached_filename(url)):
        if url not in repeated_usages:
            repeated_usages[url] = 2
        else:
            repeated_usages[url] += 1


async def cache_image(url):
    filename = get_cached_filename(url)
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


def uncache(url):
    traceback.print_stack()
    if url in repeated_usages:
        # Don't delete the image while it's still used elsewhere
        repeated_usages[url] -= 1
        if repeated_usages[url] == 1:
            del repeated_usages[url]
    else:
        try:
            filename = get_cached_filename(url)
            if os.path.isfile(filename):
                os.remove(filename)
                util.logger.info("Removed %s from image cache (no longer needed)" % url)
        except IOError as exception:
            util.logger.warning("Failed to delete cached image %s (%s)" % (url, exception))


def get_cached_filename(name):
    filename = 'assets/imagecache/' + re.sub(r'\W+', '', name)
    if len(filename) > 128:
        filename = filename[:128]
    return filename + '.jpg'


@tasks.task(timeout=10)
def save_cache_info():
    dbconn.insert_object("stats", stats)


def _load():
    collection = dbconn.get_collection_for_object(_CacheStats)
    stats_json = collection.find_one({"_id": "stats"})
    if stats_json is None:
        util.logger.info("No cache data loaded.")
    else:
        stats_data = json.loads(stats_json["data"])
        repeated_usages.update(stats_data["repeated_usages"])
        print(repeated_usages)

_load()
