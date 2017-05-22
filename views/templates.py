# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse
from django.http import JsonResponse
import json


# Template classes
class CreateTemplateView(CreateView):
    def __init__(self, model, template_name, form_class, ctx=None):

        self.model = model
        self.template_name = template_name
        self.form_class = form_class
        self.ctx = ctx

    def get(self, request, *args, **kwargs):
        if self.ctx:
            return render(request, self.template_name, self.ctx)
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):

        post = request.POST
        if self.with_request:
            form = self.form_class(post, request)
        else:
            form = self.form_class(post)
        if form.is_valid():
            element = form.save()
            response = [
                element.as_json()
            ]
            response = json.dumps(response, indent=4, separators=(',', ': '))
            return HttpResponse(response, content_type="application/json")
        else:
            return JsonResponse({'status': 'false', 'message': form.error},
                                status=500)


class UpdateTemplateView(UpdateView):

    def __init__(self, model, template_name, form_class, message_not_exists,
                 element_name):

        self.template_name = template_name
        self.message_not_exists = message_not_exists
        self.model = model
        self.element_name = element_name
        self.form_class = form_class
        self.ctx = {}
        self.element = None

    def get(self, request, *args, **kwargs):

        element_id = kwargs['pk']
        element = self.model.objects.filter(pk=element_id)
        if not element:
            return JsonResponse({'status': 'false',
                                'message': self.message_not_exists},
                                status=500)
        element = element[0]
        self.element = element
        self.ctx[self.element_name] = element
        self.add_data_ctx()
        return render(request, self.template_name, self.ctx)

    def post(self, request, *args, **kwargs):
        post = request.POST
        if self.with_request:
            form = self.form_class(post, kwargs['pk'], request)
        else:
            form = self.form_class(post, kwargs['pk'])
        if form.is_valid():
            element = form.update()
            response = [
                element.as_json()
            ]
            response = json.dumps(response, indent=4, separators=(',', ': '))
            return HttpResponse(response, content_type="application/json")
        else:
            return JsonResponse({'status': 'false', 'message': form.error},
                                status=500)

    def add_data_ctx(self):
        pass


class DeleteTemplateView(DeleteView):

    def __init__(self, model, message_not_exists):
        self.model = model
        self.message_not_exists = message_not_exists

    def get(self, request, *args, **kwargs):
        pk = int(kwargs['pk'])
        element = self.model.objects.all().filter(pk=pk)
        if element:
            element.delete()
            return JsonResponse({'status': 'true', 'message': 200}, status=200)
        else:
            return JsonResponse({'status': 'false',
                                'message': self.message_not_exists}, status=500
                                )


class ListTemplateView(ListView):

    def get(self, request, *args, **kwargs):
        elements = self.model.objects.all()
        response = [
            element.as_json()

            for element in elements
        ]
        response = json.dumps(response, indent=4, separators=(',', ': '))
        return HttpResponse(response, content_type="application/json")


class DetailTemplateView(DetailView):

    def get(self, request, *args, **kwargs):

        element_id = kwargs.get('pk', None)
        element = self.model.objects.filter(pk=element_id)
        if element:
            element = element[0]
            response = [
                element.as_json()
            ]
            response = json.dumps(response, indent=4, separators=(',', ': '))
            return HttpResponse(response, content_type="application/json")
        else:
            return JsonResponse(
                {'status': 'false', 'message': self.message_not_exists},
                status=500)


class FilterTemplateView(ListView):

    def get(self, request, *args, **kwargs):
        filter = self.filter(request)
        elements = filter.results()
        response = [
            element.as_json()
            for element in elements
        ]
        response = json.dumps(response, indent=4, separators=(',', ': '))
        return HttpResponse(response, content_type="application/json")
