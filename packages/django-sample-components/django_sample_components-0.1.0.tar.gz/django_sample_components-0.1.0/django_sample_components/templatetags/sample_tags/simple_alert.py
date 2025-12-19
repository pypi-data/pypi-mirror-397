from django.template.loader import render_to_string
from django.utils.safestring import SafeString


def simple_alert(
    content: SafeString,
    type: str = 'info',
):
    """
    Renders a simple alert box with the given content and optional prefix text.
    Adds a Font Awesome icon based on the alert type.
    """
    match type:
        case 'info':
            alert_class = 'alert-info'
            text_class = 'text-info'
            icon_class = 'fa fa-info-circle'
        case 'warning':
            alert_class = 'alert-warning'
            text_class = 'text-warning'
            icon_class = 'fa fa-exclamation-triangle'
        case 'danger':
            alert_class = 'alert-danger'
            text_class = 'text-danger'
            icon_class = 'fa fa-times-circle'
        case 'success':
            alert_class = 'alert-success'
            text_class = 'text-success'
            icon_class = 'fa fa-check-circle'
        case _:
            alert_class = 'alert-info'
            text_class = 'text-info'
            icon_class = 'fa fa-info-circle'

    context = {
        'slot_content': content,
        'alert_class': alert_class,
        'text_class': text_class,
        'icon_class': icon_class,
    }
    return render_to_string('django_sample_components/components/simple_alert.html', context)
