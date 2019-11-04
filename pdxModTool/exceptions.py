class ModFolderNotFound(Exception):

    def __init__(self, game):
        print(f'mod folder not found for <{game}> game.')


class ModArchiveNotFound(Exception):
    pass


class HandlerDescriptorError(Exception):
    pass
