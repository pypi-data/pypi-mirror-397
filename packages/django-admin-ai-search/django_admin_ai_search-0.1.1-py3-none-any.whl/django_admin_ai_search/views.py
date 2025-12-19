"""Views for Django Admin AI Search."""

import json

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from django_admin_ai_search.services import execute_search


@staff_member_required
@require_http_methods(["POST"])
def ai_search_view(request):
    """Handle AI search requests from admin."""
    try:
        data = json.loads(request.body)
        query = data.get("query", "").strip()

        if not query:
            return JsonResponse({"success": False, "error": "Query is required"})

        result = execute_search(query)
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@staff_member_required
def ai_search_page_view(request, query=""):
    """Render the admin index page with search query in URL."""
    context = {
        **admin.site.each_context(request),
        "title": "Search" if query else admin.site.index_title,
        "subtitle": None,
        "app_list": admin.site.get_app_list(request),
    }
    return render(request, "admin/index.html", context)
