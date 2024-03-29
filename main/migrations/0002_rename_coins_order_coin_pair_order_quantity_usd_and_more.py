# Generated by Django 4.2.1 on 2023-05-27 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='coins',
            new_name='coin_pair',
        ),
        migrations.AddField(
            model_name='order',
            name='quantity_usd',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_type',
            field=models.CharField(choices=[('ask', 'Ask'), ('bit', 'Bit')], max_length=4),
        ),
    ]
