from django.views import View
from django.shortcuts import render
from .models import Post, Category, Tag, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.
class PostListView(View):
    def get(self, request):
        categoryQuery = request.GET.get('category')
        tagQuery = request.GET.get('tag')
        searchQuery = request.GET.get('search')

        posts = Post.objects.all()

        if categoryQuery:
            posts = posts.filter(category__name__iexact=categoryQuery)

        if tagQuery:
            posts = posts.filter(tags__name__iexact=tagQuery)

        if searchQuery:
            posts = posts.filter(
                Q(title__icontains=searchQuery) |
                Q(content__icontains=searchQuery)|
                Q(author__username__icontains=searchQuery)|
                Q(category__name__icontains=searchQuery)|
                Q(tags__name__icontains=searchQuery)|
                Q(comments__content__icontains=searchQuery)
            ).distinct()

        paginator = Paginator(posts, 5)  # Show 5 posts per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'posts': page_obj,
            'category': categoryQuery,
            'tag': tagQuery,
            'search': searchQuery,
        }

        return render(request, 'post_list.html', context)

class PostDetailView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False) # commit=False mane temporary save. database e save korbe na
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)

        comments = post.comments.all().order_by('-created_date')

        context = {
            'post': post,
            'comments': comments,
            'comment_form': comment_form,
        }

        return render(request, 'post_detail.html', context)
    
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.view_count += 1
        liked_by_user = False
        if request.user.is_authenticated:
            if post.liked_by.filter(id=request.user.id).exists():
                liked_by_user = True
        post.save()

        comments = post.comments.all().order_by('-created_date')
        comment_form = CommentForm()

        context = {
            'post': post,
            'comments': comments,
            'comment_form': comment_form,
            'liked_by_user': liked_by_user,
        }

        return render(request, 'post_detail.html', context)

class ToggleLikeView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        if request.user.is_authenticated:
            if post.liked_by.filter(id=request.user.id).exists():
                post.liked_by.remove(request.user)
            else:
                post.liked_by.add(request.user)
            post.save()

        return redirect('post_detail', pk=post.pk)
    
class CreatePostView(View):
    def get(self, request):
        form = PostForm()
        return render(request, 'create_post.html', {'form': form})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('post_detail', pk=post.pk)
        return render(request, 'create_post.html', {'form': form})

class EditPostView(View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = PostForm(instance=post)
        return render(request, 'edit_post.html', {'form': form, 'post': post})

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
        return render(request, 'edit_post.html', {'form': form, 'post': post})

class DeletePostView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return redirect('post_list')
