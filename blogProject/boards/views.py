# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urllib
import json
from functools import wraps
from .forms import NewTopicForm, PostForm, BoardForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Board, Topic, Post, Action, Reader
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from boards.models import User
from accounts.decorators import reader_required, reporter_required
from .tasks import send_email_with_post_to_user
# Create your views here.


def check_recaptcha(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        request.recaptcha_is_valid = None
        if request.method == 'POST':
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.load(response)

            if result['success']:
                request.recaptcha_is_valid = True
                messages.success(request, 'New topic added with success!')
            else:
                request.recaptcha_is_valid = False
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def get_pages(request, queryset):
    paginator = Paginator(queryset, 20)
    page = request.GET.get('page', 1)
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        # fallback to the first page
        pages = paginator.page(1)
    except EmptyPage:
        # probably the user tried to add a page number
        # in the url, so we fallback to the last page
        page = request.GET.get('page', 1)
        pages = paginator.page(paginator.num_pages)
    return pages


class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_reader:
            queryset = Board.objects.filter(is_deleted=False, subject__in=user.reader.interests.all())
        else:
            queryset = Board.objects.filter(is_deleted=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BoardListView, self).get_context_data(**kwargs)
        actions = Action.objects.order_by('-created_at')[:10]
        context['actions'] = actions
        return context


@receiver(post_save, sender=Board)
def add_action_in_history(sender, instance, created, update_fields, **kwargs):

    if created:
        action = 'add'

    elif update_fields is not None:
        if 'is_deleted' in update_fields:
            action = 'del'
    else:
        action = 'edt'

    Action.objects.create(action=action, board=instance)


def get_history(request):
    data = dict()
    actions = Action.objects.order_by('-created_at')[:10]
    context = {'actions': actions}
    data['history_html'] = render_to_string('includes/history.html', context, request)
    return JsonResponse(data)


@reporter_required
def save_board_form(request, form, template_name, event):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            board = form.save(commit=False)
            board.creater = request.user
            board.save()
            data['form_is_valid'] = True

            if event == 'create':
                messages.success(request, '{} board created!'.format(board.name))
            elif event == 'edit':
                messages.info(request, 'Changes in {} saved!'.format(board.name))
            else:
                messages.error(request, '{} board deleted!'.format(board.name))

            boards = Board.objects.filter(is_deleted=False)
            data['html_board_list'] = render_to_string('includes/boards.html', {
                'boards': boards},
                request=request)
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


@login_required
def create_board(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)
    else:
        form = BoardForm()
    return save_board_form(request=request, form=form, template_name='includes/modal_form.html', event='create')


@login_required
def edit_board(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
    else:
        form = BoardForm(instance=board)
    return save_board_form(request=request, form=form, template_name='includes/modal_edit_form.html', event='edit')


@login_required
def delete_board(request, pk):
    data = dict()
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        board.is_deleted = True
        board.save(update_fields=['is_deleted'])
        data['form_is_valid'] = True
        messages.error(request, '{} board deleted!'.format(board.name))
        boards = Board.objects.filter(is_deleted=False)
        data['html_board_list'] = render_to_string('includes/boards.html', {
             'boards': boards},
             request=request)
    else:
        data['form_is_valid'] = False
    data['html_form'] = render_to_string('includes/modal_delete_form.html',
                                         {'board': board}, request=request)
    return JsonResponse(data)


def board_topics(request, pk):

    board = get_object_or_404(Board, pk=pk)
    queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 20)
    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        # fallback to the first page
        topics = paginator.page(1)
    except EmptyPage:
        # probably the user tried to add a page number
        # in the url, so we fallback to the last page
        topics = paginator.page(paginator.num_pages)

    return render(request, 'topics.html', {'board': board, 'topics': topics})


@check_recaptcha
@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid() and request.recaptcha_is_valid:
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()
            send_email_with_post_to_user(url='topic_post_url', email=request.user.email, post=post.message)
            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=int(topic.get_page_count())
            )
            send_email_with_post_to_user(url=topic_post_url, email=request.user.email, post=post.message)

            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@login_required
def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        data = dict()
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            topic.last_updated = timezone.now()
            topic.save()

            queryset = topic.posts.order_by('created_at')
            posts = get_pages(request, queryset)
            context = {'topic': topic, 'posts': posts}

            data['html_new_posts'] = render_to_string('includes/posts.html',
                                                      context=context,
                                                      request=request)
            current_url = request.build_absolute_uri()
            send_email_with_post_to_user(url=current_url, email=request.user.email, post=post.message)
            data['form_is_valid'] = True
            form = PostForm()
        else:
            data['form_is_valid'] = False
        context = {'topic': topic, 'form': form}

        data['html_form'] = render_to_string('includes/form.html',
                                             context=context,
                                             request=request)

        return JsonResponse(data)

    else:
        form = PostForm()
        topic.views += 1
        topic.save()

    queryset = topic.posts.order_by('created_at')
    posts = get_pages(request, queryset)
    return render(request, 'topic_posts.html', {'topic': topic, 'posts': posts, 'form': form})


class NewPostView(CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('post_list')
    template_name = 'new_post.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super(PostUpdateView, self).get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super(TopicListView, self).get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset
