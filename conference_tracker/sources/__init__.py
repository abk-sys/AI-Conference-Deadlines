from . import opencurious

# A directory adapter returns only {id, website, directory_sources} records.
DIRECTORY_ADAPTERS = {'opencurious_directory': opencurious.fetch}
