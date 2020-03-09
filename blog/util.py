
def paginate(iterator, page=0, size=None):
    """
    paginates an iterator, returning the pageth page of size size.
    size=None -> page size is unbounded
    """
    assert(size != 0)

    if size is None:
        yield from iterator
        return

    for i, obj in enumerate(iterator):
        if i >= (page+1)*size:
            break

        if i >= page*size:
            yield obj
