# Generated by Django 3.0.3 on 2020-03-03 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('run_duel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fightevent',
            name='round',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='run_duel.Round'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='round',
            name='duel',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='run_duel.Duel'),
            preserve_default=False,
        ),
    ]
