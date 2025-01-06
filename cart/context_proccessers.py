def search_context(request):
    return {
        'search_term': request.GET.get('search', '')  # Get the search term from the request
    }