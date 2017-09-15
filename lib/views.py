from django.shortcuts import render, render_to_response
from django.core.urlresolvers import reverse_lazy
from .models import Pouch, Person, Category, Staff
from django.views import generic

class PersonView(generic.ListView):
    template_name = 'lib/person.html'
    context_object_name = 'person'

    def get_queryset(self):
        return Person.objects.order_by('firstname')

class PersonEdit(generic.UpdateView):
    model = Person
    success_url = reverse_lazy('lib:person')
    fields = ['firstname', 'secondname']
    template_name = 'lib/edit_create_form.html'

class PersonCreate(generic.CreateView):
    model = Person
    success_url = reverse_lazy('lib:person')
    fields = ['firstname', 'secondname']
    template_name = 'lib/edit_create_form.html'

class PersonDelete(generic.DeleteView):
    model = Person
    success_url = reverse_lazy('lib:person')
    template_name = 'lib/confirm_delete.html'

def PouchView(request):
    user = request.user
    user_id = user.pk
    staff = Staff.objects.get(name__id=user_id)
    permitted_pouches = [x for x in staff.pouches.all()]
    pouch = Pouch.objects.filter(name__in=permitted_pouches)
    template = 'lib/pouch.html'
    context = {
        'user': user,
        'pouch': pouch,
    }
    return render_to_response(template, context)


class PouchEdit(generic.UpdateView):
    model = Pouch
    template_name = 'lib/edit_create_form.html'
    success_url = reverse_lazy('lib:pouch')
    fields = ['name', 'type', 'comment']

class PouchCreate(generic.CreateView):
    model = Pouch
    template_name = 'lib/edit_create_form.html'
    success_url = reverse_lazy('lib:pouch')
    fields = ['name', 'starting_balance', 'type', 'comment']

class PouchDelete(generic.DeleteView):
    model = Pouch
    success_url = reverse_lazy('lib:pouch')
    template_name = 'lib/confirm_delete.html'

class CategoryView(generic.ListView):
    template_name = 'lib/category.html'
    context_object_name = 'category'

    def get_queryset(self):
        return Category.objects.order_by('name')

class CategoryEdit(generic.UpdateView):
    model = Category
    template_name = 'lib/edit_create_form.html'
    success_url = reverse_lazy('lib:category')
    fields = ['name']

class CategoryCreate(generic.CreateView):
    model = Category
    template_name = 'lib/edit_create_form.html'
    success_url = reverse_lazy('lib:category')
    fields = ['name']

class CategoryDelete(generic.DeleteView):
    model = Category
    success_url = reverse_lazy('lib:category')
    template_name = 'lib/confirm_delete.html'



