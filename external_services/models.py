from django.db import models
from shared_config.models import ModelBase

class ApiRequestLog(ModelBase):
    """
    Model to track api request response
    """
    path = models.CharField(max_length=200, help_text="url path")
    remote_addr = models.GenericIPAddressField(null=True)
    host = models.URLField(null=True)
    query_param = models.TextField(null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    errors = models.TextField(null=True, blank=True)
    response_ms = models.PositiveIntegerField(default=0)
    cached = models.BooleanField(default=False)
    status_code = models.PositiveIntegerField(null=True, blank=True)
    service_name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.path, self.status_code)
    
    class Meta:
        db_table = 'external_apirequestlog'
        managed = False
        app_label = 'external'


class ApiExternalLog(ModelBase):
    """
    Model to track any third party api call
    """
    request_log = models.ForeignKey(ApiRequestLog, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=200, null=True, blank=True)
    service_url = models.URLField()
    request_body = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)
    is_valid_response = models.BooleanField(default=False)

    def __str__(self):
        return "{} {}".format(self.service_name, self.status_code)

    class Meta:
        db_table = 'external_apiexternallog'
        managed = False
        app_label = 'external'