# Fix tenant FK: integer → UUID (AIONETRA tenants.Tenant uses UUID PK).
# 0008에서 AUTH_USER_MODEL(integer) 기반으로 생성된 컬럼을 교체.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookstudio', '0008_tenant_support'),
        ('tenants', '0001_initial'),
    ]

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
                to='tenants.tenant',
                db_index=True,
            ),
        ),
    ]
