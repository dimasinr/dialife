from django import template

register = template.Library()

STATUS_STYLES = {
    'stable': 'bg-primary/10 text-primary border border-primary/20',
    'warning': 'bg-secondary-fixed text-on-secondary-fixed-variant',
    'critical': 'bg-error-container text-on-error-container',
    'pending': 'bg-surface-variant text-on-surface-variant',
}

STATUS_BAR = {
    'stable': 'bg-primary',
    'warning': 'bg-secondary-container',
    'critical': 'bg-error',
    'pending': 'bg-surface-variant',
}

SEVERITY_BORDER = {
    'critical': 'border-l-error',
    'warning': 'border-l-secondary',
    'info': 'border-l-primary',
}


@register.filter
def status_badge_class(status):
    return STATUS_STYLES.get(status, STATUS_STYLES['stable'])


@register.filter
def status_bar_class(status):
    return STATUS_BAR.get(status, STATUS_BAR['stable'])


@register.filter
def severity_border_class(severity):
    return SEVERITY_BORDER.get(severity, SEVERITY_BORDER['info'])


@register.filter
def fluid_bar_width(patient):
    return min(patient.fluid_percent, 100)
