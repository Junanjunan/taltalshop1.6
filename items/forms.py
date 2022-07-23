from django import forms
from . import models


class ItemCreatingForm(forms.ModelForm):
    class Meta:
        model = models.Item
        fields = (
            'item_category',
            'name',
            'price',
            'deli_fee',
            'rocket',
            'producer',
            'coo',
            'precaution',
            'inquiry_number',
            'certification',
            'quality_guarantee',
            'how_to_use',
            'volume',
            'cosmetic_component',
            'use_period',
            'specification',
            'item_model_name',
            'about_electric',
            'release_date',
            'youtube_url',
        )

    def save(self):
        item = super().save(commit=False)
        return item


class ItemUpdatingForm(forms.ModelForm):
    class Meta:
        model = models.Item
        fields = (
            'item_category',
            'name',
            'price',
            'deli_fee',
            'rocket',
            'producer',
            'coo',
            'precaution',
            'inquiry_number',
            'certification',
            'quality_guarantee',
            'how_to_use',
            'volume',
            'cosmetic_component',
            'use_period',
            'specification',
            'item_model_name',
            'about_electric',
            'release_date',
            'youtube_url',
        )

    def save(self):
        item = super().save(commit=False)
        return item


class ItemPhotoCreatingForm(forms.ModelForm):
    class Meta:
        model = models.ItemPhoto
        fields = ('photo', 'name')

    def save(self):
        itemPhoto = super().save(commit=False)
        return itemPhoto


class ItemPhotoMultipleCreatingForm(forms.Form):
    class Meta:
        model = models.ItemPhoto
        fields = ('photo', 'name')
        file_field = forms.FileField(
            widget=forms.ClearableFileInput(attrs={'multiple': True})
            )

    def save(self):
        itemPhoto = super().save(commit=False)
        return itemPhoto

class ItemDetailPageCreatingForm(forms.ModelForm):
    class Meta:
        model = models.ItemDetailPage
        fields = ('photo', 'name')
    
    def save(self):
        detail_page = super().save(commit=False)
        return detail_page

class InquiryCreatingForm(forms.ModelForm):
    class Meta:
        model = models.Inquiry
        fields = ('inquiry',)
        widgets = {
            'inquiry': forms.Textarea(attrs={'rows': 10, 'cols': 60})
        }


    def save(self):
        inquiry = super().save(commit=False)
        return inquiry
