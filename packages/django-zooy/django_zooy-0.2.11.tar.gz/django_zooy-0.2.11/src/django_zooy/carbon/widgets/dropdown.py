from django.forms import widgets

from .base import CarbonWidgetMixin


class CarbonDropdown(CarbonWidgetMixin, widgets.Select):
    """
    Carbon Design System dropdown widget for Django forms.

    Uses <cds-dropdown> web component with <cds-dropdown-item> children.

    Documentation:
    https://web-components.carbondesignsystem.com/?path=/docs/components-dropdown

    Example usage:
        class MyForm(CarbonFormMixin, forms.Form):
            network = forms.ChoiceField(
                choices=NETWORK_CHOICES,
                widget=CarbonDropdown()
            )

    For dropdowns inside modals or near the bottom of containers, use
    direction="top" to make the dropdown open upward:

        widget=CarbonDropdown(attrs={"direction": "top"})

    Attributes:
        direction: "top" or "bottom" (default). Controls which direction
                   the dropdown menu opens. Use "top" for dropdowns near
                   the bottom of modals to prevent clipping.
        type: "default" or "inline". Use inline for dropdowns placed
              inline with other content.
        size: "sm", "md" (default), or "lg". Controls option spacing.
    """

    template_name = "django_zooy/carbon/widgets/dropdown.html"

    # Dropdown direction
    # Use "top" for dropdowns near the bottom of modals to prevent clipping
    DIRECTION_BOTTOM = "bottom"
    DIRECTION_TOP = "top"

    # Dropdown types
    # Sometimes you will need to place a dropdown inline with other content.
    # To do that, add type="inline" to the dropdown.
    TYPE_DEFAULT = "default"
    TYPE_INLINE = "inline"

    # Dropdown sizes
    # This drives the space between the options in the dropdown list
    SIZE_SMALL = "sm"
    SIZE_MEDIUM = "md"
    SIZE_LARGE = "lg"
