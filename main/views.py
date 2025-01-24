from django.http import JsonResponse
from .models import Article
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.conf import settings


def get_articles(request):
    free_articles_limit = 5  # халява
    articles = Article.objects.all().values('id', 'title', 'author', 'publication_date', 'tags', 'free')

    
    free_articles = articles.filter(free=True)[:free_articles_limit]

    # для зареганных 
    if request.user.is_authenticated:
        paid_articles = articles.filter(free=False)
    else:
        paid_articles = []

    response_data = {
        "status": "success",
        "data": {
            "free_articles": list(free_articles),
            "paid_articles": list(paid_articles),
        },
    }
    return JsonResponse(response_data)

@login_required
def get_article_by_id(request, id):
    try:
        article = Article.objects.get(id=id)
        if not article.free and not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Требуется авторизация для просмотра этой статьи"}, status=403)
        return JsonResponse({"status": "success", "data": {
            'id': article.id,
            'title': article.title,
            'author': article.author,
            'publication_date': article.publication_date,
            'tags': article.tags,
            'content': article.content,
            'free': article.free
        }})
    except Article.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Article not found"}, status=404)


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if not (name and email and message):
            return JsonResponse({"status": "error", "message": "Заполните все поля."}, status=400)

        send_mail(
            subject=f"Новое сообщение от {name}",
            message=f"Email: {email}\n\nСообщение:\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,  # значение из settings.py
            recipient_list=[settings.CONTACT_EMAIL],  #  переменная для получателя
        )

        return JsonResponse({"status": "success", "message": "Ваше сообщение успешно отправлено."})
    
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)


def about(request):
    return JsonResponse({"status": "success", "data": {"content": "Информация о нас"}})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Вход пользователя после регистрации
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)

            return redirect('home')  # Перенаправление на главную страницу или другую страницу

    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(user.pk.encode('utf-8'))

    # Создание ссылки с токеном
    verification_link = request.build_absolute_uri(f'/verify/{uid}/{token}/')

    # Отправка письма
    send_mail(
        subject="Подтверждение email",
        message=f"Перейдите по следующей ссылке для подтверждения email: {verification_link}",
        from_email="noreply@example.com",  # Ваш email
        recipient_list=[user.email],
    )

def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')  # Перенаправление на главную страницу
    else:
        return redirect('invalid_token')  # Если токен неправильный
