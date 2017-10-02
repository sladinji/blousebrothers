from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.conf import settings


from oscar.core.loading import get_model
from django_weasyprint.views import PDFTemplateResponseMixin


Order = get_model('order', 'Order')


class PDFView(LoginRequiredMixin, DetailView):
    template_name = "dashboard/orders/pdf.html"
    model = Order
    object_name = "order"
    print_btn = True

    def get_context_data(self, **kwargs):
        return super().get_context_data(print_btn=self.print_btn, **kwargs)


class PDFViewPrintView(PDFTemplateResponseMixin, PDFView):
    print_btn = False

    def get_filename(self):
        return "facture_{0.number}.pdf".format(self.object)
