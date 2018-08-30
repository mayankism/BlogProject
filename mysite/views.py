from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from blog.models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from .forms import ContactForm
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import messages


def post_list(request):
    object_list = Post.published.all().order_by("-publish")
    query = request.GET.get("q")
    if query:
        object_list = object_list.filter(Q(title__icontains=query)|
                                         Q(body__icontains=query)

                                         ).distinct()
    paginator = Paginator(object_list, 5)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    template = 'blog/post/list.html'
    context = {
        'posts': posts,
        'page': page,
    }
    return render(request, template, context )


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
            status='published',
            publish__year=year,
            publish__month=month,
            publish__day=day)
    comments = post.comments.filter(approved_comment=False)
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.post = post
                new_comment.save()
        messages.add_message(request, messages.INFO, 'Hello world.')
    else:
        comment_form = CommentForm
    template = 'blog/post/detail.html',
    context ={
        'post': post,
        'comments': comments,
        'comment_form': comment_form}
    return render(request, template, context)

def contact(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        name = form.cleaned_data['name']
        comment = form.cleaned_data['comment']
        subject = 'Message from Be Inspired blog'
        message = '%s %s' %(comment, name)
        emailfrom= form.cleaned_data['email']
        emailTo = [settings.EMAIL_HOST_USER]
        send_mail(subject, message, emailfrom, emailTo, fail_silently=False)
        messages.success(request, 'Profile updated successfully')
    context = {'form': form}
    return render(request, 'blog/post/contact.html', context)


def terms(request):
    return render(request, 'blog/post/terms.html', {})



