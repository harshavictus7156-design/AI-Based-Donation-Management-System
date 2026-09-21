from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("donor", "0001_initial"),
    ]

    operations = [

        # -------------------------------------------------
        # Rename old purpose field to item_name
        # -------------------------------------------------

        migrations.RenameField(
            model_name="donation",
            old_name="purpose",
            new_name="item_name",
        ),

        # -------------------------------------------------
        # Remove old amount field
        # -------------------------------------------------

        migrations.RemoveField(
            model_name="donation",
            name="amount",
        ),

        # -------------------------------------------------
        # Add NGO
        # -------------------------------------------------

        migrations.AddField(
            model_name="donation",
            name="ngo",
            field=models.ForeignKey(
                to="donor.ngo",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="donations",
                null=True,
                blank=True,
            ),
        ),

        # -------------------------------------------------
        # Category
        # -------------------------------------------------

        migrations.AddField(
            model_name="donation",
            name="category",
            field=models.CharField(
                max_length=50,
                choices=[
                    ("Clothing", "Clothing"),
                    ("Books", "Books"),
                    ("Food", "Food"),
                    ("Electronics", "Electronics"),
                    ("Furniture", "Furniture"),
                    ("Medical Supplies", "Medical Supplies"),
                    ("School Supplies", "School Supplies"),
                    ("Other", "Other"),
                ],
                default="Other",
            ),
            preserve_default=False,
        ),

        # -------------------------------------------------
        # Quantity
        # -------------------------------------------------

        migrations.AddField(
            model_name="donation",
            name="quantity",
            field=models.PositiveIntegerField(
                default=1
            ),
            preserve_default=False,
        ),

        # -------------------------------------------------
        # Condition
        # -------------------------------------------------

        migrations.AddField(
            model_name="donation",
            name="condition",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("New", "New"),
                    ("Like New", "Like New"),
                    ("Good", "Good"),
                    ("Used", "Used"),
                ],
                default="Good",
            ),
            preserve_default=False,
        ),

        # -------------------------------------------------
        # Description
        # -------------------------------------------------

        migrations.AddField(
            model_name="donation",
            name="description",
            field=models.TextField(
                default=""
            ),
            preserve_default=False,
        ),

        # -------------------------------------------------
        # Location
        # -------------------------------------------------

        migrations.AddField(
            model_name="donation",
            name="location",
            field=models.CharField(
                max_length=200,
                default=""
            ),
            preserve_default=False,
        ),

        # -------------------------------------------------
        # Item Image
        # -------------------------------------------------

        migrations.AddField(
            model_name="donation",
            name="item_image",
            field=models.ImageField(
                upload_to="donation_items/",
                null=True,
                blank=True,
            ),
        ),

        # -------------------------------------------------
        # Status
        # -------------------------------------------------

        migrations.AddField(
            model_name="donation",
            name="status",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("Pending", "Pending"),
                    ("Accepted", "Accepted"),
                    ("Rejected", "Rejected"),
                    ("Collected", "Collected"),
                ],
                default="Pending",
            ),
        ),
    ]