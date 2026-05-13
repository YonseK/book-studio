# Fix tenant FK: integer → UUID (AIONETRA tenants.Tenant uses UUID PK).
# 0008에서 AUTH_USER_MODEL(integer) 기반으로 생성된 컬럼을 교체.
# TENANT_MODEL이 설정되지 않은 환경에서는 no-op.

import django.db.models.deletion
from django.db import migrations, models

from bookstudio import conf

_tenant_model = conf.TENANT_MODEL  # e.g. "tenants.Tenant" or None


def _tenant_app_label():
    if _tenant_model:
        return _tenant_model.split(".")[0]
    return None


class Migration(migrations.Migration):

    dependencies = [
        ('bookstudio', '0008_tenant_support'),
    ] + (
        [(_tenant_app_label(), '0001_initial')] if _tenant_model else []
    )

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='tenant',
        ),
        migrations.AddField(
            model_name='book',
            name='tenant',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='bookstudio_books_by_tenant',
                to=_tenant_model or 'auth.User',
                db_index=True,
            ),
        ),
    ] if _tenant_model else []
