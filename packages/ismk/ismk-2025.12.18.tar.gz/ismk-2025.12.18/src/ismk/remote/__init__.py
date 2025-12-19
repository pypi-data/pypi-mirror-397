# remote providers have been replaced by storage plugins, see
# https://github.com/ismk/ismk-interface-storage-plugins


class RemoteProviderBase:
    def __init__(self, *args, **kwargs):
        # TODO add URL to plugin documentation/catalog
        raise NotImplementedError(
            "Remote providers have been replaced by SMK storage plugins. Please "
            "use the corresponding storage plugin instead (ismk-storage-plugin-*)."
        )
