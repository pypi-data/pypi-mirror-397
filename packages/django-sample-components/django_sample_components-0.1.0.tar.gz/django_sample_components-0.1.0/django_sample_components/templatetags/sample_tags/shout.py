from django.utils.safestring import SafeString, mark_safe


def shout(content: SafeString, bg_color=None):
    return mark_safe(f"<h2 style='text-transform:uppercase; background-color:{bg_color}'>{content}!!!!</h2>")
