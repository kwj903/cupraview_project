from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .forms import LoginForm, UserForm, UserUpdateForm, DeleteAccountForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .models import Ramen, Review, User
from django.contrib.auth import logout as django_logout


def welcome(request):
    return render(request, "welcome.html")


def main_page(request):  # 메인 페이지: 좋아요 수 기준 상위 10개의 라면 보여줌
    top_ramen = Ramen.objects.order_by("-like_number")[
        :10
    ]  # like_number 기준 내림차순 정렬 후 상위 10개 추출
    return render(
        request, "main_page.html", {"top_ramen": top_ramen}
    )  # 템플릿에 라면 리스트 전달하여 렌더링


# 로그인 뷰
def user_login(request):  # 로그인 처리
    form = LoginForm(
        request.POST or None
    )  # POST 방식이면 전달된 데이터 바탕으로 폼 생성

    if request.method == "POST":  # POST 요청일 경우만 로그인 시도
        if form.is_valid():  # 폼 유효성 검사 통과 시
            email = form.cleaned_data["email"]  # 이메일 추출
            password = form.cleaned_data["password"]  # 비밀번호 추출

            try:
                user = User.objects.get(email=email)  # 해당 이메일로 유저 검색
                if check_password(password, user.password):  # 비밀번호 확인
                    request.session["user_id"] = user.id  # 세션에 유저 정보 저장
                    request.session["user_nickname"] = user.nickname
                    request.session["user_email"] = user.email
                    return redirect("main_page")  # 메인 페이지로 이동
                else:
                    form.add_error(
                        None, "비밀번호가 틀렸습니다."
                    )  # 비밀번호 오류 메시지 추가
            except User.DoesNotExist:
                form.add_error(
                    "email", "이메일이 존재하지 않습니다."
                )  # 이메일 오류 메시지 추가

    return render(request, "user/login.html", {"form": form})  # 로그인 폼 렌더링


# 회원가입 뷰
def user_signup(request):  # 회원가입 처리
    if request.method == "POST":  # POST 요청일 경우에만 회원가입 시도
        form = UserForm(request.POST)  # 폼 생성
        if form.is_valid():  # 유효성 검사 통과 시
            email = form.cleaned_data["email"]
            nickname = form.cleaned_data["nickname"]
            password = form.cleaned_data["password1"]

            # 이메일 중복 확인
            if User.objects.filter(email=email).exists():
                form.add_error("email", "이미 사용 중인 이메일입니다.")
                return render(request, "user/signup.html", {"form": form})

            # 닉네임 중복 확인
            if User.objects.filter(nickname=nickname).exists():
                form.add_error("nickname", "이미 사용 중인 닉네임입니다.")
                return render(request, "user/signup.html", {"form": form})

            # 유저 생성
            hashed_pw = make_password(password)  # 비밀번호 해싱
            User.objects.create(
                email=email, nickname=nickname, password=hashed_pw
            )  # 유저 생성

            messages.success(request, "회원가입이 완료되었습니다.")
            return redirect("ramen_login")  # 로그인 페이지로 이동
    else:
        form = UserForm()  # GET 요청이면 빈 폼 생성

    return render(request, "user/signup.html", {"form": form})  # 폼 렌더링


# 회원정보수정
def update_profile(request):  # 유저 프로필 수정
    user_id = request.session.get("user_id")  # 세션에서 유저 ID 가져오기
    if not user_id:
        return redirect("ramen_login")  # 로그인 안 했으면 로그인 페이지로

    user = User.objects.get(id=user_id)  # 현재 로그인한 유저 정보 가져오기

    if request.method == "POST":  # POST 요청이면 수정 시도
        form = UserUpdateForm(
            request.POST, instance=user
        )  # 기존 유저 정보 바탕으로 폼 생성
        if form.is_valid():
            email = form.cleaned_data["email"]
            nickname = form.cleaned_data["nickname"]
            password1 = form.cleaned_data.get("password1")
            password2 = form.cleaned_data.get("password2")

            # 이메일/닉네임 중복 검사 (자기 자신은 제외)
            email_exists = User.objects.exclude(id=user.id).filter(email=email).exists()
            nickname_exists = (
                User.objects.exclude(id=user.id).filter(nickname=nickname).exists()
            )

            if email_exists:
                form.add_error("email", "이미 사용 중인 이메일입니다.")
            elif nickname_exists:
                form.add_error("nickname", "이미 사용 중인 닉네임입니다.")
            else:
                user.email = email
                user.nickname = nickname

                if password1 and password2:
                    user.password = make_password(password1)  # 비밀번호 변경 시 해싱

                user.save()  # 수정 사항 저장
                user = User.objects.get(id=user_id)  # 갱신된 정보 다시 가져오기
                request.session["user_id"] = user.id
                request.session["user_nickname"] = user.nickname
                request.session["user_email"] = user.email
                messages.success(request, "회원정보가 수정되었습니다.")
                return redirect("main_page")
    else:
        form = UserUpdateForm(instance=user)  # GET 요청이면 기존 정보로 폼 생성

    return render(request, "user/update_profile.html", {"form": form})


# 회원탈퇴 뷰
def delete_account(request):  # 회원 탈퇴 처리
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("ramen_login")

    user = User.objects.get(id=user_id)
    form = DeleteAccountForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            password = form.cleaned_data["password1"]

            if not check_password(password, user.password):  # 비밀번호 검증 실패 시
                form.add_error("password1", "비밀번호가 일치하지 않습니다.")
                return render(request, "user/delete_account.html", {"form": form})

            user.delete()  # 유저 삭제
            request.session.flush()  # 세션 초기화
            messages.success(request, "회원 탈퇴가 완료되었습니다.")
            return redirect("ramen_login")
        else:
            return render(request, "user/delete_account.html", {"form": form})

    return render(request, "user/delete_account.html", {"form": form})


# 로그아웃
def logout(request):  # 로그아웃 처리
    # form = UserForm(request.POST or None)
    django_logout(request)  # Django의 로그아웃 함수로 세션 삭제
    return redirect("main_page")  # 메인페이지로 이동


# 검색기능
def search(request):  # 라면 이름 검색 기능
    query = ""
    results = []

    if request.method == "POST":
        query = request.POST.get("query", "")  # 검색어 가져오기
        if query:
            results = Ramen.objects.filter(
                ramen_name__icontains=query
            )  # 이름에 검색어 포함된 라면 필터링

    return render(request, "search.html", {"results": results, "query": query})


# 라면 디테일 뷰
def ramen_detail(request, ramen_id):  # 라면 상세페이지 뷰
    user_id = request.session.get("user_id")
    ramen = get_object_or_404(Ramen, pk=ramen_id)  # 라면 정보 가져오기

    review_to_edit = None
    if "edit" in request.GET:
        review_to_edit = get_object_or_404(
            Review, pk=request.GET["edit"]
        )  # 리뷰 수정 시 기존 리뷰 불러오기

    if request.method == "POST":
        content = request.POST["content"]  # 리뷰 내용 추출

        if not user_id:
            messages.warning(request, "로그인이 필요합니다.")
            return redirect("ramen_login")

        user = get_object_or_404(User, id=user_id)

        if review_to_edit:  # 수정 요청일 경우
            if review_to_edit.user_id.id == user_id:
                review_to_edit.content = content
                review_to_edit.save()
                return redirect("ramen_detail", ramen_id=ramen.id)

        Review.objects.create(  # 새로운 리뷰 생성
            content=content,
            created_at=timezone.now(),
            user_id=user,
            ramen_id=ramen,
        )
        return HttpResponseRedirect(request.path_info)

    return render(
        request,
        "ramen_detail.html",
        {
            "ramen": ramen,
            "review_to_edit": review_to_edit,
        },
    )


# 리뷰 삭제 뷰
def review_delete(request, pk):  # 리뷰 삭제 처리
    user_id = request.session.get("user_id")
    review = get_object_or_404(Review, pk=pk)

    if review.user_id.id != user_id:  # 본인 리뷰만 삭제 가능
        return HttpResponse("권한이 없습니다.", status=403)

    if request.method == "POST":
        review.delete()
        return redirect("ramen_detail", ramen_id=review.ramen_id.id)

    return render(request, "ramen_detail.html", {"review": review})


# 리뷰 좋아요 뷰
def like_review_increase(request, ramen_id):  # 리뷰 좋아요 처리
    user_id = request.session.get("user_id")

    if not user_id:
        messages.warning(request, "로그인이 필요합니다.")
        return redirect("ramen_login")

    ramen = get_object_or_404(Ramen, id=ramen_id)
    liked_ramen = request.session.get(
        "liked_ramen", []
    )  # 세션에서 좋아요 누른 라면 목록 가져오기

    if ramen_id in liked_ramen:
        messages.warning(request, "이미 좋아요를 누르셨어요!")  # 중복 방지
    else:
        ramen.like_number += 1
        ramen.save()  # 좋아요 수 증가
        liked_ramen.append(ramen_id)  # 세션에 추가
        request.session["liked_ramen"] = liked_ramen
        messages.success(request, "좋아요가 반영되었습니다!")

    return HttpResponseRedirect(
        request.META.get("HTTP_REFERER", "/")
    )  # 이전 페이지로 리디렉션
