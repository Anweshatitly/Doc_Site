from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, F
from .models import BlogCategory, Tag, BlogPost


def post_list(request, category_slug=None, tag_slug=None):
    """
    Blog Listing View with:
    - Published-only query
    - Category filtering (via SEO URL or query parameter)
    - Tag filtering
    - Keyword search
    - Server-side Pagination
    - Spotlight Featured Article
    """
    categories = BlogCategory.objects.filter(is_active=True).order_by('name')
    tags = Tag.objects.all().order_by('name')

    posts = (
        BlogPost.objects.filter(status='published')
        .select_related('category', 'author')
        .prefetch_related('tags')
        .order_by('-published_at', '-created_at')
    )

    # Category filter (support URL pattern /blog/category/<slug>/ or ?category=<slug>)
    selected_cat_slug = category_slug or request.GET.get('category')
    selected_category = None
    if selected_cat_slug and selected_cat_slug != 'all':
        selected_category = get_object_or_404(BlogCategory, slug=selected_cat_slug, is_active=True)
        posts = posts.filter(category=selected_category)

    # Tag filter
    selected_tag_slug = tag_slug or request.GET.get('tag')
    selected_tag = None
    if selected_tag_slug:
        selected_tag = get_object_or_404(Tag, slug=selected_tag_slug)
        posts = posts.filter(tags=selected_tag)

    # Keyword search
    query = request.GET.get('q', '').strip()
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query)
        )

    # Featured Spotlight Post (displayed on page 1 of all posts if not searching/filtering)
    page_number = request.GET.get('page', 1)
    featured_post = None
    if str(page_number) in ('1', '') and not query and not selected_category and not selected_tag:
        featured_post = BlogPost.objects.filter(status='published', is_featured=True).first()

    # Pagination: 6 posts per page
    paginator = Paginator(posts, 6)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'categories': categories,
        'tags': tags,
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'selected_category': selected_category,
        'selected_tag': selected_tag,
        'query': query,
        'featured_post': featured_post,
        'total_count': posts.count(),
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """
    Blog Detail View with:
    - View count increment
    - Related posts in same category (backfilled if fewer than 3)
    - Recent articles sidebar
    - Category directory
    - SEO Meta tags
    """
    post = get_object_or_404(BlogPost, slug=slug, status='published')

    # Increment view count atomically
    BlogPost.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
    post.refresh_from_db(fields=['views_count'])

    # Related Posts: Same category, excluding current post
    related_posts = list(
        BlogPost.objects.filter(category=post.category, status='published')
        .exclude(pk=post.pk)
        .order_by('-published_at')[:3]
    )

    # If fewer than 3 related posts in the same category, backfill with recent published posts
    if len(related_posts) < 3:
        existing_ids = [p.pk for p in related_posts] + [post.pk]
        backfill = (
            BlogPost.objects.filter(status='published')
            .exclude(pk__in=existing_ids)
            .order_by('-published_at')[:3 - len(related_posts)]
        )
        related_posts.extend(backfill)

    # Sidebar recent posts
    recent_posts = (
        BlogPost.objects.filter(status='published')
        .exclude(pk=post.pk)
        .order_by('-published_at')[:4]
    )

    categories = BlogCategory.objects.filter(is_active=True).order_by('name')

    context = {
        'post': post,
        'related_posts': related_posts,
        'recent_posts': recent_posts,
        'categories': categories,
    }
    return render(request, 'blog/post_detail.html', context)
