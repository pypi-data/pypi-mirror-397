from django.forms import widgets
from django.utils.html import escape

from .base import CarbonWidgetMixin


class CarbonCheckbox(CarbonWidgetMixin, widgets.CheckboxInput):
    """
    Carbon Design System single checkbox widget for Django forms.

    Renders a single <cds-checkbox> element for boolean fields.

    Documentation:
    https://web-components.carbondesignsystem.com/?path=/docs/components-checkbox

    Example usage:
        class MyForm(CarbonFormMixin, forms.Form):
            agree_to_terms = forms.BooleanField(
                label="I agree to the terms",
                widget=CarbonCheckbox()
            )
    """

    template_name = "django_zooy/carbon/widgets/checkbox.html"

    def get_context(self, name, value, attrs):
        """Build context for rendering a single cds-checkbox."""
        context = super().get_context(name, value, attrs)

        # For checkboxes, we need to handle the checked state and label
        widget_attrs = context["widget"]["attrs"].copy()

        # Add label-text from the label attribute (injected by CarbonFormMixin)
        if self.attrs.get("label"):
            widget_attrs["label-text"] = self.attrs.get("label")

        # Add helper-text if present
        if self.attrs.get("helper-text"):
            widget_attrs["helper-text"] = self.attrs.get("helper-text")

        # Handle checked state - CheckboxInput sets 'checked' in attrs when value is True
        if context["widget"]["value"]:
            widget_attrs["checked"] = True

        # Handle validation states
        if self.attrs.get("invalid") is not None:
            widget_attrs["invalid"] = True
            if self.attrs.get("invalid-text"):
                widget_attrs["invalid-text"] = self.attrs.get("invalid-text")

        # Handle warning states
        if self.attrs.get("warn"):
            widget_attrs["warn"] = True
            if self.attrs.get("warn-text"):
                widget_attrs["warn-text"] = self.attrs.get("warn-text")

        # Handle disabled
        if self.attrs.get("disabled"):
            widget_attrs["disabled"] = True

        # Handle readonly
        if self.attrs.get("readonly"):
            widget_attrs["readonly"] = True

        # Rebuild attr_string with updated attributes
        context["widget"]["attr_string"] = self._build_attr_string(widget_attrs, name, "on")

        return context

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Override to not set default size for checkboxes."""
        attrs = widgets.CheckboxInput.build_attrs(self, base_attrs, extra_attrs)
        return attrs


class CarbonCheckboxSelectMultiple(CarbonWidgetMixin, widgets.CheckboxSelectMultiple):
    """
    Carbon Design System checkbox group widget for Django forms.

    Renders multiple <cds-checkbox> elements within a <cds-checkbox-group>.

    Documentation:
    https://web-components.carbondesignsystem.com/?path=/docs/components-checkbox

    Example usage:
        class MyForm(CarbonFormMixin, forms.Form):
            services = forms.MultipleChoiceField(
                choices=SERVICE_CHOICES,
                widget=CarbonCheckboxSelectMultiple()
            )
    """

    template_name = "django_zooy/carbon/widgets/checkbox_select_multiple.html"
    option_template_name = "django_zooy/carbon/widgets/checkbox_option.html"

    def get_context(self, name, value, attrs):
        """Build context including group-level attributes for cds-checkbox-group."""
        context = super().get_context(name, value, attrs)

        # Build group attributes for <cds-checkbox-group>
        # Note: For CheckboxSelectMultiple, CarbonFormMixin injects into self.attrs
        # rather than the attrs parameter passed to get_context
        group_attrs_parts = []

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

        # Orientation (vertical is default, so only add if horizontal)
        orientation = self.attrs.get("orientation")
        if orientation == "horizontal":
            group_attrs_parts.append('orientation="horizontal"')

        context["widget"]["group_attrs"] = " ".join(group_attrs_parts)

        return context
