from django.forms import widgets
from django.utils.html import escape

from .base import CarbonWidgetMixin


class CarbonDatePicker(CarbonWidgetMixin, widgets.DateInput):
    """
    Carbon Design System date picker widget for Django forms.

    Renders a <cds-date-picker> with a <cds-date-picker-input> child.

    Documentation:
    https://web-components.carbondesignsystem.com/?path=/docs/components-date-picker

    Example usage:
        class MyForm(CarbonFormMixin, forms.Form):
            start_date = forms.DateField(
                widget=CarbonDatePicker()
            )

    Attributes:
        date_format: Flatpickr date format string (default: 'Y-m-d' for ISO format)
        allow_input: Allow manual input (default: True)
        close_on_select: Close picker when date is selected (default: True)
        placeholder: Input placeholder text (default: 'yyyy-mm-dd')

    Note:
        The date picker uses Flatpickr internally. The date_format attribute
        follows Flatpickr's format tokens:
        - Y: 4-digit year (2024)
        - m: 2-digit month (01-12)
        - d: 2-digit day (01-31)

        Django's DateField uses ISO format (YYYY-MM-DD) by default, which
        corresponds to Flatpickr's 'Y-m-d' format.
    """

    template_name = "django_zooy/carbon/widgets/date_picker.html"

    # Default date format (ISO 8601)
    DEFAULT_DATE_FORMAT = "Y-m-d"
    DEFAULT_PLACEHOLDER = "yyyy-mm-dd"

    def __init__(self, attrs=None, date_format_str=None):
        """
        Initialize the date picker widget.

        Args:
            attrs: Widget attributes
            date_format_str: Django date format string (for form handling, not display)
        """
        super().__init__(attrs=attrs, format=date_format_str)

    def get_context(self, name, value, attrs):
        """Build context for rendering the date picker."""
        context = super().get_context(name, value, attrs)

        # Build picker-level attributes
        picker_attrs = {}

        # Date format for Flatpickr
        picker_attrs["date-format"] = self.attrs.get("date_format", self.DEFAULT_DATE_FORMAT)

        # Allow manual input
        if self.attrs.get("allow_input", True):
            picker_attrs["allow-input"] = True

        # Close on select
        if self.attrs.get("close_on_select", True):
            picker_attrs["close-on-select"] = True

        # Handle min/max dates
        if self.attrs.get("min_date"):
            picker_attrs["min-date"] = self.attrs.get("min_date")
        if self.attrs.get("max_date"):
            picker_attrs["max-date"] = self.attrs.get("max_date")

        # Handle disabled dates
        if self.attrs.get("disabled_dates"):
            picker_attrs["disabled-dates"] = self.attrs.get("disabled_dates")

        # Handle readonly
        if self.attrs.get("readonly"):
            picker_attrs["readonly"] = True

        # Handle disabled
        if self.attrs.get("disabled"):
            picker_attrs["disabled"] = True

        # Build input-level attributes
        input_attrs = {}

        # Kind is always 'single' for single date picker
        input_attrs["kind"] = "single"

        # Name for form submission
        input_attrs["name"] = name

        # Label text
        if self.attrs.get("label"):
            input_attrs["label-text"] = self.attrs.get("label")

        # Helper text
        if self.attrs.get("helper-text"):
            input_attrs["helper-text"] = self.attrs.get("helper-text")

        # Placeholder
        input_attrs["placeholder"] = self.attrs.get("placeholder", self.DEFAULT_PLACEHOLDER)

        # Size
        input_attrs["size"] = self.attrs.get("size", "md")

        # Handle required
        if self.attrs.get("required"):
            input_attrs["required"] = True

        # Handle validation states
        if self.attrs.get("invalid") is not None:
            input_attrs["invalid"] = True
            if self.attrs.get("invalid-text"):
                input_attrs["invalid-text"] = self.attrs.get("invalid-text")

        # Handle warning states
        if self.attrs.get("warn"):
            input_attrs["warn"] = True
            if self.attrs.get("warn-text"):
                input_attrs["warn-text"] = self.attrs.get("warn-text")

        # ID for the input
        if attrs and attrs.get("id"):
            input_attrs["id"] = attrs.get("id")

        # Value (pre-populated date)
        if value:
            # Format the value as a string if it's a date object
            if hasattr(value, "strftime"):
                value = value.strftime("%Y-%m-%d")
            input_attrs["value"] = value

        # Build attribute strings
        context["widget"]["picker_attrs"] = self._build_picker_attrs(picker_attrs)
        context["widget"]["input_attrs"] = self._build_input_attrs(input_attrs)

        return context

    def _build_picker_attrs(self, attrs):
        """Build HTML attribute string for the picker element."""
        parts = []
        for key, val in attrs.items():
            if val is True:
                parts.append(key)
            elif val is not False and val is not None:
                parts.append(f'{key}="{escape(str(val))}"')
        return " ".join(parts)

    def _build_input_attrs(self, attrs):
        """Build HTML attribute string for the input element."""
        parts = []
        for key, val in attrs.items():
            if val is True:
                parts.append(key)
            elif val is not False and val is not None:
                parts.append(f'{key}="{escape(str(val))}"')
        return " ".join(parts)

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Override to not set default size at picker level."""
        attrs = widgets.DateInput.build_attrs(self, base_attrs, extra_attrs)
        return attrs
