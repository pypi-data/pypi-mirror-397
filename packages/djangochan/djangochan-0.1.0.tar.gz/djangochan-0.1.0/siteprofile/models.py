# By @pydatageek under CC BY-SA 4.0
# https://stackoverflow.com/a/64288644
from django.contrib.sites.models import Site
from django.db import models


class SiteProfileBase(models.Model):
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="profile",
        verbose_name="site",
    )

    class Meta:
        abstract = True
        db_table = "sites_siteprofile"


## in core.models
# from siteprofile.models import SiteProfileBase
# class SiteProfile(SiteProfileBase):
#     field = ...
