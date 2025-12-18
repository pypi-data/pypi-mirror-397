def is_magic(k: str) -> bool:
    return (k.startswith("__") and k.endswith("__")) or (k == "_abc_impl")
