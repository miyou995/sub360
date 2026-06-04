import csv
from io import BytesIO

import pandas as pd
import weasyprint
from django.http import HttpResponse, StreamingHttpResponse
from django.utils import timezone


def format_date(field):
    return field.apply(lambda a: timezone.localtime(a).strftime("%Y-%m-%d %H:%M:%S"))
    # return field.apply(lambda a: datetime.strftime(a, "%Y-%m-%d %H:%M:%S"))


class Echo:
    def write(self, value):
        return value


class DataExporter:
    def __init__(self, queryset, columns):
        self.queryset = queryset
        self.columns = columns
        self.data = self.prepare_data()

    def prepare_data(self):
        data = pd.DataFrame(list(self.queryset), columns=self.columns)
        if "created_at" in data:
            data["created_at"] = format_date(data["created_at"])
        if "updated_at" in data:
            data["updated_at"] = format_date(data["updated_at"])
        return data

    def export_to_excel(self, file_name):
        filename = f"{file_name}-{timezone.now().date()}.xlsx"
        with BytesIO() as b:
            with pd.ExcelWriter(b, engine="openpyxl") as writer:
                self.data.to_excel(writer, sheet_name="Data", index=False, header=True)
            res = HttpResponse(
                b.getvalue(),
                content_type="application/vnd.ms-excel",
            )
            res["Content-Disposition"] = f"attachment; filename={filename}"
        return res

    def export_to_csv(self, file_name):
        filename = f"{file_name}-{timezone.now().date()}.csv"

        def csv_generator():
            echo_buffer = Echo()
            writer = csv.writer(echo_buffer, delimiter=";", quoting=csv.QUOTE_MINIMAL)
            yield writer.writerow(self.columns)

            for row in self.data.itertuples(index=False):
                yield writer.writerow(row)

        response = StreamingHttpResponse(csv_generator(), content_type="text/csv")
        response["Content-Disposition"] = f'attachment;filename="{filename}"'
        return response

    def export_to_pdf(self, file_name):
        filename = f"{file_name}-{timezone.now().date()}.pdf"
        html_file = self.data.to_html(index=False, justify="left")
        pdf_file = weasyprint.HTML(string=html_file).write_pdf()
        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment;filename="{filename}"'
        return response
