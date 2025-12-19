from django.forms import widgets
from django.utils.html import escape

from .base import CarbonWidgetMixin


class CarbonRadioSelect(CarbonWidgetMixin, widgets.RadioSelect):
    """
    Carbon Design System radio button group widget for Django forms.

    Renders a <cds-radio-button-group> with <cds-radio-button> children.

    Documentation:
    https://web-components.carbondesignsystem.com/?path=/docs/components-radio-button

    Example usage:
        class MyForm(CarbonFormMixin, forms.Form):
            file_format = forms.ChoiceField(
                choices=[('csv', 'CSV'), ('xlsx', 'Excel')],
                widget=CarbonRadioSelect()
            )

    Attributes:
        orientation: 'horizontal' or 'vertical' (default: 'vertical')
    """

    template_name = "django_zooy/carbon/widgets/radio_select.html"
    option_template_name = "django_zooy/carbon/widgets/radio_option.html"

    # Orientation options
    ORIENTATION_VERTICAL = "vertical"
    ORIENTATION_HORIZONTAL = "horizontal"

    def get_context(self, name, value, attrs):
        """Build context including group-level attributes for cds-radio-button-group."""
        context = super().get_context(name, value, attrs)

        # Build group attributes for <cds-radio-button-group>
        group_attrs_parts = []

        # Name attribute for the group
        group_attrs_parts.append(f'name="{escape(name)}"')

        # Get label for legend-text (injected by CarbonFormMixin into self.attrs)
        if self.attrs.get("label"):
            group_attrs_parts.append(f'legend-text="{escape(self.attrs.get("label"))}"')

        # Get help text (injected by CarbonFormMixin as 'helper-text' into self.attrs)
        if self.attrs.get("helper-text"):
            group_attrs_parts.append(f'helper-text="{escape(self.attrs.get("helper-text"))}"')

        # Handle required state
        if self.attrs.get("required"):
            group_attrs_parts.append("required")

        # Handle validation states (injected by CarbonFormMixin after validation)
        if self.attrs.get("invalid") is not None:
            group_attrs_parts.append("invalid")
            if self.attrs.get("invalid-text"):
                group_attrs_parts.append(f'invalid-text="{escape(self.attrs.get("invalid-text"))}"')

        # Handle warning states
        if self.attrs.get("warn"):
            group_attrs_parts.append("warn")
            if self.attrs.get("warn-text"):
                group_attrs_parts.append(f'warn-text="{escape(self.attrs.get("warn-text"))}"')

        # Handle readonly
        if self.attrs.get("readonly"):
            group_attrs_parts.append("readonly")

        # Handle disabled (injected by CarbonFormMixin)
        if self.attrs.get("disabled"):
            group_attrs_parts.append("disabled")

        # Orientation (vertical is default)
        orientation = self.attrs.get("orientation", self.ORIENTATION_VERTICAL)
        group_attrs_parts.append(f'orientation="{escape(orientation)}"')

        context["widget"]["group_attrs"] = " ".join(group_attrs_parts)

        return context

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Override to not set default size for radio buttons."""
        attrs = widgets.RadioSelect.build_attrs(self, base_attrs, extra_attrs)
        return attrs
