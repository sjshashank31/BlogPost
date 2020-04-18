from django.shortcuts import render, get_object_or_404, redirect,reverse
from django.views.generic import ListView, View
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin, ContextMixin
from users.models import Post,Comment
from users.forms import CommentForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# def index(request):
  # context1 = {'post': Post.objects.all()}
   # return render(request, 'home.html', context1)


class PostListView(ListView):
    model = Post
    template_name = 'home.html'
    paginate_by = 12
    context_object_name = 'post'
    ordering = ['date_published']


class BlogView(FormMixin, DetailView, ContextMixin):
    model = Post
    template_name = 'blogview.html'
    pk_and_query = True
    form_class = CommentForm

    def get_success_url(self):
        return reverse('home:blog', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm(initial={'post': self.object})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        post_title = get_object_or_404(Post, slug=self.object.slug)
        post_qs = Post.objects.filter(user=self.object.user)
        form = self.get_form()

        if post_qs.exists():
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

    def form_valid(self, form):
        post = Post.objects.get(slug=self.object.slug)
        comment = Comment.objects.create(user=self.object.user, post_title=post, comment=self.request.POST['comment'])
        comment.save()
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        post = Post.objects.get(post_title=self.object.post_title)
        comment_qs = Comment.objects.filter(post_title=post)
        if comment_qs.exists():
            context['comments'] = Comment.objects.filter(post_title=post).all()
            print(context['comments'])
            return context
        return context


@login_required
def user_view(request):
    context = {}
    context['post'] = Post.objects.filter(user=request.user).all()
    return render(request, 'blogger.html',context )
