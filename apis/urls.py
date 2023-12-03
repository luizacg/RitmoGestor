from django.urls import path, include
import apis.views as api_view
from django.contrib import admin


urlpatterns = [
    path('details/', api_view.DetailView.as_view()),
    path('frequencia/', api_view.FrequenciaView.as_view()),
    path('pontuacoes/', api_view.PontuacoesView.as_view()),
    path('timetable/', api_view.TimetableView.as_view()),
]
