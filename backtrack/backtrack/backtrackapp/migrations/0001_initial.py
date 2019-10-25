# Generated by Django 2.2.6 on 2019-10-22 22:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProductBacklogItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('desc', models.TextField()),
                ('priority', models.PositiveIntegerField()),
                ('storypoints', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('NS', 'Not Started'), ('IP', 'In Progress'), ('C', 'Complete')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('desc', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('available', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('desc', models.TextField()),
                ('burndown', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('NS', 'Not Started'), ('IP', 'In Progress'), ('C', 'Complete')], max_length=1)),
                ('assignment', models.ManyToManyField(to='backtrackapp.User')),
                ('pbi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backtrackapp.ProductBacklogItem')),
            ],
        ),
        migrations.AddField(
            model_name='productbacklogitem',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backtrackapp.Project'),
        ),
    ]