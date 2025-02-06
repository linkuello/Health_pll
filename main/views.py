from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Article
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings


def get_articles(request):
    free_articles_limit = 5  # максимальное количество бесплатных статей
    articles = Article.objects.all().values('id', 'title', 'author', 'publication_date', 'tags', 'free')

    # Бесплатные статьи
    free_articles = articles.filter(free=True)[:free_articles_limit]

    # Платные статьи для авторизованных пользователей
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
    article = get_object_or_404(Article, id=id)
    # Платные статьи доступны только зарегистрированным пользователям
    if article.free or request.user.is_authenticated:
        return render(request, 'main/article_detail.html', {'article': article})
    else:
        return JsonResponse({"status": "error", "message": "Эта статья доступна только зарегистрированным пользователям."}, status=403)


def home(request):
    return render(request, 'main/home.html')  # Убедитесь, что файл home.html существует


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
            recipient_list=[settings.CONTACT_EMAIL],  # переменная для получателя
        )

        return JsonResponse({"status": "success", "message": "Ваше сообщение успешно отправлено."})
    
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


def about(request):
    return render(request, 'main/about.html')
