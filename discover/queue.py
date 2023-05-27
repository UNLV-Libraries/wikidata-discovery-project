from django.db.models import QuerySet
queue = []  # a list of lists

def add_request(req: object) -> None:
    global queue
    queue.insert(0, req)

    if queue.__len__() > 3:  # Restrict queue length to 3
        queue.pop()

def get_request(key: int) -> list:
    global queue
    obj = queue.pop(key)  # get entire queue entry
    queue.insert(0, obj)  # reinsert at top of queue, since it's now the most recent query
    return obj

def post_from_queue(key: int) -> object:
    req = queue[key]
    req_obj = req[0]
    return req_obj

def update_query(query: QuerySet, n) -> None:
    # adds query object to specified list in queue
    # following form processing
    global queue
    queue[n][2] = query


def set_prior_queries() -> list:
    # creates list of choices for prior query form
    the_choices = [(0, ' ---- ')]
    n = 1
    for i in queue:
        the_choices.append((n, i[1]))
        n += 1
    return the_choices
