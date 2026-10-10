from . import opencurious

# Each adapter implements fetch(config, client) -> list of normalized records.
ADAPTERS = {'opencurious': opencurious.fetch}
