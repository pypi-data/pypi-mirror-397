import zipfile
import os
from pathlib import Path

from django.conf import settings

from weasyprint import HTML


def generate_summary(instance, output_field: str = "summary"):

    html = "<html><body><h1>MARINERG-i Access Application</h1>"
    html += "<h2>Applicant</h2>"
    html += f"<p>{instance.applicant.first_name} {instance.applicant.last_name}</p>"
    html += f"<p>Email: {instance.applicant.email}</p>"

    html += "<h2>Access Call</h2>"
    html += f"<p>{instance.call.title}</p>"

    requested_facilities = instance.facilities.all()
    if requested_facilities:
        html += "<h2>Requested Facilities</h2>"
        for facility in requested_facilities:
            html += f"<p>{facility.name}</p>"

    if instance.chosen_facility:
        html += "<h2>Chosen Facility</h2>"
        html += f"<p>{instance.chosen_facility.name}</p>"

    html += "<h2>Dates</h2>"
    if instance.request_start_date:
        html += f"<p>Requested Start Date: {str(instance.request_start_date)}</p>"
    if instance.request_end_date:
        html += f"<p>Requested End Date: {str(instance.request_end_date)}</p>"
    html += f"<p>Dates Flexible: {instance.dates_flexible}</p>"

    html += "<h2>Custom Fields</h2>"
    for value in instance.form.values.all():
        if value.field.field_type != "FILE":
            html += f"<p>{value.field.label}: {value.value}</p>"

    html += "</body></html>"

    pdf_bytes = HTML(string=html).write_pdf()

    field_path = f"{instance._meta.model_name}_{output_field}"
    work_dir = Path(settings.MEDIA_ROOT) / field_path
    os.makedirs(work_dir, exist_ok=True)

    filename = f"{field_path}_{instance.id}.zip"
    with zipfile.ZipFile(
        work_dir / filename, "w", zipfile.ZIP_DEFLATED, False
    ) as zip_file:
        for value in instance.form.values.all():
            if value.field.field_type == "FILE" and value.asset:
                zip_file.write(
                    Path(settings.MEDIA_ROOT) / value.asset.name,
                    arcname=f"{value.field.label}.pdf",
                )
        zip_file.writestr("summary.pdf", pdf_bytes)

    instance.summary.name = os.path.join(field_path, filename)
