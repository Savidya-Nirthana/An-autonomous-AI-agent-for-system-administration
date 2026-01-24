DELETE_PENDING = {}


def store_delete_request(session_id: str, path: str):
    DELETE_PENDING[session_id] = path


def get_delete_request(session_id: str):
    return DELETE_PENDING.get(session_id, None)


def clear_delete_request(session_id: str):
    if session_id in DELETE_PENDING:
        del DELETE_PENDING[session_id]


    