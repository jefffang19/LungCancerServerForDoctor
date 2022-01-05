from django import forms


class UploadFileForm(forms.Form):
    age = forms.CharField(max_length=50)
    SEX_CHOICE = (
        (1, ("Female")),
        (2, ("Male")),
        (3, ("Other")),
    )
    gender = forms.ChoiceField(choices=SEX_CHOICE)
    tumer_location = forms.CharField(max_length=200)
    file = forms.FileField()
