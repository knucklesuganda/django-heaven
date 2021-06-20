from django.db import migrations, models


class Migration(migrations.Migration):
    operations = [
        migrations.CreateModel(
            name='HeavenTestModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name='name')),
                ('creation_date', models.DateTimeField(auto_now=True)),
                ('is_working', models.BooleanField(default=True)),
            ],
        ),
    ]
