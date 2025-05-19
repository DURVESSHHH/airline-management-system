from django.db import models

class Report(models.Model):
    title = models.CharField(max_length=100)
    report_type = models.CharField(
        max_length=50,
        choices=[
            ('Sales', 'Sales'),
            ('Performance', 'Performance'),
            ('Operations', 'Operations'),
        ]
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Store structured data instead of plain text

    def __str__(self):
        return f"{self.title} - {self.report_type}"
