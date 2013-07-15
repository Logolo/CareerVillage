from django.db import models


class FacebookObject(models.Model):
    """ Facebook app-owned object.
    """
    app = models.CharField(max_length=100)
    model_id = models.IntegerField()  # Local ID

    object_type = models.CharField(max_length=255)  # Type used to create the object (does not include app namespace)
    object_id = models.BigIntegerField()  # Facebook ID

    class Meta:
        unique_together = ('app', 'object_type', 'model_id')
        app_label = 'forum'
