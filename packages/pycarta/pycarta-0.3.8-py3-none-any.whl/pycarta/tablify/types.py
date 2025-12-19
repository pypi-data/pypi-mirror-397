class EMPTY:
    """
    Custom sentinel separate from None
    
    Used to indicate that an entry has not been created as opposed to
    the entry is null.
    """
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # def __iter__(self):
    #     return self

    # def __next__(self):
    #     raise StopIteration()
    
    # def __len__(self):
    #     return 0

    def __str__(self):
        return "EMPTY"

    def __repr__(self):
        return "EMPTY"

    @staticmethod
    def fill(container, /, replacement=None):
        # Edits the container in place, replacing EMPTY with None.
        if isinstance(container, list):
            for i, x in enumerate(container):
                if x is EMPTY():
                    container[i] = replacement
                else:
                    EMPTY.fill(container[i])
        elif isinstance(container, dict):
            for k, v in container.items():
                if v is EMPTY():
                    container[k] = replacement
                else:
                    EMPTY.fill(container[k])
