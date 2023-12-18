from multiprocessing.dummy import Pool

pool: Pool = None

def get_pool() -> Pool:
    global pool
    if not pool:
        pool = Pool(6)

    return pool