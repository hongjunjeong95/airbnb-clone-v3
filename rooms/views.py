from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage
from . import models as room_models


def homeView(request):
    try:
        # Get list of rooms
        rooms_list = room_models.Room.objects.all()

        # Get paginator
        page = int(request.GET.get("page", 1))
        page_sector = (page - 1) // 5
        page_sector = page_sector * 5
        paginator = Paginator(rooms_list, 12, orphans=6)
        rooms = paginator.get_page(page)
    except EmptyPage:
        print("Empty page")

    return render(
        request,
        "pages/root/home.html",
        context={"rooms": rooms, "page_sector": page_sector},
    )
