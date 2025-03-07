# Generated by Django 5.1.7 on 2025-03-07 06:50

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('delivered', 'Delivered')], default='pending', help_text='Current status of the order', max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, help_text='Total price of the order', max_digits=10, null=True),
        ),
        migrations.AlterModelTable(
            name='order',
            table='ORDERS',
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('product_id', models.CharField(max_length=36)),
                ('quantity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='order_app.order')),
            ],
        ),
    ]
