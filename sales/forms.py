from __future__ import annotations

from typing import Any

from django import forms

from .models import Warehouse


class WarehouseForm(forms.ModelForm):
    """Form for creating a warehouse."""

    class Meta:
        model = Warehouse
        fields = ['name', 'warehouse_type', 'marketplace', 'is_primary']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full border-gray-300 rounded-xl',
            }),
            'warehouse_type': forms.Select(attrs={
                'class': 'block w-full border-gray-300 rounded-xl',
            }),
            'marketplace': forms.Select(attrs={
                'class': 'block w-full border-gray-300 rounded-xl',
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-primary border-gray-300 rounded',
            }),
        }

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        warehouse_type = cleaned_data.get('warehouse_type')
        marketplace = cleaned_data.get('marketplace')

        if warehouse_type == 'MARKETPLACE_FF' and not marketplace:
            self.add_error('marketplace', 'Укажите маркетплейс для склада фулфилмента.')

        if warehouse_type != 'MARKETPLACE_FF':
            cleaned_data['marketplace'] = None

        return cleaned_data
