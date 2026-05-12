from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginate(objects_list, request, per_page=20):
    paginator = Paginator(objects_list, per_page)

    page_num = request.GET.get('page', 1)

    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(1)

    return page
