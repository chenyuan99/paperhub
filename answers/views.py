from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, JsonResponse
from django.views import generic
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from gettingstarted.settings import logger
from asks.models import Ask
from .models import Answer


class IndexView(generic.DetailView):
    template_name = 'index.html'

    def get_object(self, queryset=None):
        answers_list = Answer.objects.order_by('-create_time')
        paginator = Paginator(answers_list, 10)
        return paginator

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        asks = Ask.objects.all().order_by('-create_time')[:5]
        vote_list = []
        collection_list = []
        context['asks'] = asks
        context['answers'] = self.object.page(1)
        context['explore'] = True
        if self.request.user.is_authenticated:
            for answer in self.object.page(1):
                if self.request.user.is_voted(answer):
                    vote_list.append(answer)
                if self.request.user.is_collected(answer):
                    collection_list.append(answer)
        context['vote_list'] = vote_list
        context['collection_list'] = collection_list
        return context

    def get(self, request, *args, **kwargs):
        super(IndexView, self).get(request, *args, **kwargs)
        page = request.GET.get('page', None)
        if page is None:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

        vote_list = []
        collection_list = []
        try:
            answers = self.object.page(page)
        except PageNotAnInteger or EmptyPage:
            return HttpResponseNotFound
        if self.request.user.is_authenticated:
            for answer in self.object.page(page):
                if self.request.user.is_voted(answer):
                    vote_list.append(answer)
                if self.request.user.is_collected(answer):
                    collection_list.append(answer)
        context = dict(answers=answers, vote_list=vote_list, collection_list=collection_list)
        return render(request, 'answerslist.html', context)


class CreateAnswerView(LoginRequiredMixin, generic.CreateView):
    model = Answer
    fields = ['content', 'content_text']

    def form_valid(self, form):
        ask_id = self.kwargs['pk']
        ask = Ask.objects.filter(id=ask_id).first()
        user = self.request.user
        if ask is not None:
            answer = form.save(commit=False)
            answer.ask = ask
            answer.author = user
            answer.save()
            logger.info('{} 回答了问题 : {}'.format(self.request.user, answer))
        return redirect(self.request.META.get('HTTP_REFERER', '/'))

    def form_invalid(self, form):
        logger.error('answer error')
        return redirect(self.request.META.get('HTTP_REFERER', '/'))


class DeleteAnswerView(LoginRequiredMixin, generic.DeleteView):
    model = Answer

    def get_success_url(self):
        logger.info('答案：{} 删除成功'.format(self.object.id))
        return self.request.META.get('HTTP_REFERER', '/')


class ShowAnswerView(generic.DetailView):
    model = Answer

    def get(self, request, *args, **kwargs):
        data = dict(r=1)
        try:
            answer = Answer.objects.get(id=kwargs['pk'])
        except Answer.DoesNotExist:
            return JsonResponse(data)
        data['r'] = 0
        data['content'] = answer.content
        data['create_time'] = answer.create_time.date()
        return JsonResponse(data)


class SearchView(generic.DetailView):
    template_name = 'index.html'

    def get_object(self, queryset=None):
        key_word = self.request.GET.get('s', '')
        answers_list = Answer.objects.filter(Q(content_text__icontains=key_word)
                                             | Q(ask__title__icontains=key_word)).order_by('-votes')
        paginator = Paginator(answers_list, 10)
        return paginator

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        asks = Ask.objects.all().order_by('-create_time')[:5]
        vote_list = []
        collection_list = []
        context['asks'] = asks
        context['answers'] = self.object.page(1)
        context['explore'] = True
        if self.request.user.is_authenticated:
            for answer in self.object.page(1):
                if self.request.user.is_voted(answer):
                    vote_list.append(answer)
                if self.request.user.is_collected(answer):
                    collection_list.append(answer)
        context['vote_list'] = vote_list
        context['collection_list'] = collection_list
        return context

    def get(self, request, *args, **kwargs):
        super(SearchView, self).get(request, *args, **kwargs)
        page = request.GET.get('page', None)
        if page is None:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

        vote_list = []
        collection_list = []
        try:
            answers = self.object.page(page)
        except PageNotAnInteger or EmptyPage:
            return HttpResponseNotFound
        if self.request.user.is_authenticated:
            for answer in self.object.page(page):
                if self.request.user.is_voted(answer):
                    vote_list.append(answer)
                if self.request.user.is_collected(answer):
                    collection_list.append(answer)
        context = dict(answers=answers, vote_list=vote_list, collection_list=collection_list)
        return render(request, 'answerslist.html', context)


@login_required
def vote_up(request, pk):
    data = dict(
        r=1,
    )
    if request.method == 'POST':
        user = request.user
        answer = Answer.objects.filter(id=pk).first()
        if answer is not None:
            ret = user.voteup(answer)
            if ret is True:
                data['r'] = 0
                data['count'] = answer.votes
                logger.info('{} 赞同了： {}'.format(user, answer.id))
            else:
                logger.error('{} 赞同失败: {}'.format(user, answer.id))
    return JsonResponse(data, status=201)


@login_required
def vote_down(request, pk):
    data = dict(
        r=1,
    )
    if request.method == 'POST':
        user = request.user
        answer = Answer.objects.filter(id=pk).first()
        if answer is not None:
            ret = user.votedown(answer)
            if ret is True:
                data['r'] = 0
                data['count'] = answer.votes
                logger.info('{} 取消了赞： {}'.format(user, answer.id))
            else:
                logger.error('{} 取消赞失败: {}'.format(user, answer.id))
    return JsonResponse(data, status=201)


@login_required
def collect(request, pk):
    data = dict(
        r=1,
    )
    if request.method == 'POST':
        user = request.user
        answer = Answer.objects.filter(id=pk).first()
        if answer is not None:
            ret = user.collect(answer)
            if ret is True:
                data['r'] = 0
                logger.info('{} 收藏了： {}'.format(user, answer.id))
            else:
                logger.error('{} 收藏失败: {}'.format(user, answer.id))
    return JsonResponse(data, status=201)


@login_required
def uncollect(request, pk):
    data = dict(
        r=1,
    )
    if request.method == 'POST':
        user = request.user
        answer = Answer.objects.filter(id=pk).first()
        if answer is not None:
            ret = user.uncollect(answer)
            if ret is True:
                data['r'] = 0
                logger.info('{} 取消了收藏： {}'.format(user, answer.id))
            else:
                logger.error('{} 取消收藏失败: {}'.format(user, answer.id))
    return JsonResponse(data, status=201)