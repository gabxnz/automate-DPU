def user_enrolment_created(data):
    if not isinstance(data, dict):
        return None
    return data.get('relateduserid') or data.get('userid')


def user_enrolment_updated(data):
    if not isinstance(data, dict):
        return None
    return data.get('relateduserid') or data.get('userid')