import markdown2
from django.shortcuts import render, redirect
from django import forms
import random


from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })

    html_content = markdown2.markdown(content)

    return render(request, "encyclopedia/entry.html", {
        "title": title,            # ✅ this must be passed
        "content": html_content
    })

def search(request):
    query = request.GET.get("q", "")  # get text from search bar
    entries = util.list_entries()     # all available pages
    
    # If query matches an entry exactly, show that page
    if query in entries:
        return redirect("entry", title=query)
    
    # Otherwise, show a results page with partial matches
    results = [entry for entry in entries if query.lower() in entry.lower()]
    return render(request, "encyclopedia/search.html", {
        "query": query,
        "results": results
    })

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea, label="Content")

def new_page(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # Check if page already exists
            if util.get_entry(title) is not None:
                return render(request, "encyclopedia/error.html", {
                    "message": f"An entry with the title '{title}' already exists."
                })

            # Save the new entry
            util.save_entry(title, content)
            return redirect("entry", title=title)
    else:
        form = NewPageForm()

    return render(request, "encyclopedia/new_page.html", {
        "form": form
    })

class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 10, "cols": 80}))

def edit(request, title):
    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect("entry", title=title)   # ✅ redirect to entry, not index
    else:
        content = util.get_entry(title)
        if content is None:
            return render(request, "encyclopedia/error.html", {
                "message": "Page not found."
            })
        form = EditForm(initial={"content": content})

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": form
    })

def random_page(request):
    entries = util.list_entries()
    if not entries:
        return render(request, "encyclopedia/error.html", {
            "message": "No pages available."
        })

    title = random.choice(entries)
    return redirect("entry", title=title)        
    