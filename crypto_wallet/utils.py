from django.db.models import Model


def get_or_none(class_: Model, **kwargs):
    try:
        return class_.objects.get(**kwargs)
    except class_.DoesNotExist:
        pass
    except class_.MultipleObjectsReturned:
        return []
    return None
