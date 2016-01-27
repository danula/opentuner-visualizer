from django import forms
from django.forms import ModelForm
from visualizer.models import Project, Analysis


class CustomUserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_name()
    

class AnalysisForm(ModelForm):
    name = forms.CharField()
    project = CustomUserChoiceField(queryset=Project.objects.all())
    method = forms.ChoiceField(choices=(
        ('remove_param', 'Remove Parameters'), ('compare_bin', 'Compare Binaries'), ('random_forest', 'Random Forest'),
        ('relief', 'Relief')))

    class Meta:
        model = Analysis
