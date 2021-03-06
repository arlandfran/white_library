# Generated by Django 4.0.2 on 2022-02-28 03:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('products', '0005_remove_product_author_remove_product_book_format_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'base_manager_name': 'objects'},
        ),
        migrations.AlterModelOptions(
            name='boxedset',
            options={'base_manager_name': 'objects'},
        ),
        migrations.AlterModelOptions(
            name='collectible',
            options={'base_manager_name': 'objects'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'base_manager_name': 'objects'},
        ),
        migrations.AddField(
            model_name='product',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype'),
        ),
    ]
