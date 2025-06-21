from django import forms

from ramen.models import User


class LoginForm(forms.Form):
    email = forms.EmailField(label="이메일")
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput)


class UserForm(forms.ModelForm):
    password1 = forms.CharField(label="비밀번호", widget=forms.PasswordInput)
    password2 = forms.CharField(label="비밀번호 확인", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "nickname"]
        labels = {
            "email": "이메일",
            "nickname": "닉네임",
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        if password1 and len(password1) < 8:
            raise forms.ValidationError( "비밀번호는 8자 이상이어야 합니다.")
        return cleaned_data


class UserUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="새 비밀번호", widget=forms.PasswordInput, required=False
    )
    password2 = forms.CharField(
        label="새 비밀번호 확인", widget=forms.PasswordInput, required=False
    )

    class Meta:
        model = User
        fields = ["email", "nickname"]
        labels = {
            "email": "이메일",
            "nickname": "닉네임",
        }

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password1")
        pw2 = cleaned_data.get("password2")

        if pw1 or pw2:
            if not pw1 or not pw2:
                raise forms.ValidationError("비밀번호를 모두 입력해주세요.")
            if pw1 != pw2:
                raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
            if pw1 and len(pw1) < 8:
                raise forms.ValidationError( "비밀번호는 8자 이상이어야 합니다.")   

        return cleaned_data


class DeleteAccountForm(forms.Form):
    password1 = forms.CharField(label="비밀번호", widget=forms.PasswordInput)
    password2 = forms.CharField(label="비밀번호 확인", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password1")
        pw2 = cleaned_data.get("password2")

        if not pw1 or not pw2:
            raise forms.ValidationError("비밀번호를 모두 입력해주세요.")

        if pw1 != pw2:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")

        return cleaned_data
