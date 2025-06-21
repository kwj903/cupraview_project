from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .models import Ramen, Review, User
from django.contrib.auth import logout as django_logout


# Create your views here.
def main_page(request):
    top_ramen = Ramen.objects.order_by("-like_number")[:10]
    return render(request, "main_page.html", {"top_ramen": top_ramen})


# 로그인 뷰
def user_login(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            try:
                user = User.objects.get(email=email)
                if check_password(password, user.password):
                    request.session["user_id"] = user.id  # 수동 로그인
                    request.session["user_nickname"] = user.nickname # 세션에 닉네임 넣기
                    return redirect("main_page")  # 로그인 성공시 이동할 경로
                # user = authenticate(request, username=user.username, password=password)
                # if user is not None:
                #     login(request, user)
                #     return redirect("home")
                else:
                    form.add_error(None, "비밀번호가 틀렸습니다.")
            except User.DoesNotExist:
                form.add_error("email", "이메일이 존재하지 않습니다.")

    return render(request, "user/login.html", {"form": form})


# 회원가입 뷰
def user_signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        nickname = request.POST.get("nickname")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # 1. 비어있는 값 확인
        if not (email and nickname and password1 and password2):
            messages.error(request, "모든 항목을 입력해주세요.")
            return render(request, "user/signup.html")

        # 2. 비밀번호 확인
        if password1 != password2:
            messages.error(request, "비밀번호가 일치하지 않습니다.")
            return render(request, "user/signup.html")

        # 3. 이메일 중복 확인
        if User.objects.filter(email=email).exists():
            messages.error(request, "이미 존재하는 이메일입니다.")
            return render(request, "user/signup.html")

        # 4. 닉네임 중복 확인
        if User.objects.filter(nickname=nickname).exists():
            messages.error(request, "이미 존재하는 닉네임입니다.")
            return render(request, "user/signup.html")

        # 5. 유저 생성 (비밀번호는 해시로)
        hashed_pw = make_password(password1)
        User.objects.create(email=email, nickname=nickname, password=hashed_pw)

        messages.success(request, "회원가입이 완료되었습니다. 로그인해주세요.")
        return redirect("ramen_login")  # 로그인 경로로 리디렉션

    return render(request, "user/signup.html")


# 회원탈퇴 뷰
def delete_account(request):
    user_id = request.session.get("user_id")

    if not user_id:
        # 로그인 안 한 사용자
        return redirect("ramen_login")  # 로그인 페이지로

    if request.method == "POST":
        try:
            user = User.objects.get(id=user_id)
            user.delete()  # DB에서 삭제
            request.session.flush()  # 세션 초기화 (로그아웃)
            return redirect("ramen_login")  # 탈퇴 후 이동할 페이지
        except User.DoesNotExist:
            pass  # 혹시 삭제 도중 문제가 생기면 무시

    return render(request, "user/delete_account.html")  # GET 요청 시 페이지 보여주기

# 로그아웃
def logout(request):
    django_logout(request)  # 세션에서 사용자 정보 삭제
    return redirect("main_page")  # 메인페이지로 이동


def search(request):  # 컵라면 이름을 검색
    query = request.GET.get("query", "")
    results = []  # 빈 리스트. 검색했을때 db정보를 처음에는 숨기기 위해

    if query:  # 검색어가 있을 때만 데이터베이스에서 검색
        results = Ramen.objects.filter(ramen_name__icontains=query)  # 검색 결과

    return render(request, "search.html", {"results": results, "query": query})


# 승아
def ramen_detail(request, ramen_id):
    user_id = request.session.get("user_id")
    ramen = get_object_or_404(Ramen, pk=ramen_id)

    if request.method == "POST":
        content = request.POST["content"]
        user = User.objects.get(id=user_id)
        # ramen은 위에서 이미 get 했으니 재사용 가능!

        Review.objects.create(
            content=content,
            created_at=timezone.now(),
            user_id=user,
            ramen_id=ramen,
        )

        return HttpResponseRedirect(request.path_info)

    # GET 요청일 경우 렌더링
    ramens = Ramen.objects.all()
    return render(
        request, "ramen_detail.html", {"ramen": ramen, "ramens": ramens}  # select box용
    )


def like_review_increase(request, like_number):
    ramen = get_object_or_404(Ramen, id=id)
    ramen.like_number += 1
    ramen.save()
    return HttpResponse({"ramen_like_number": ramen.like_number})
