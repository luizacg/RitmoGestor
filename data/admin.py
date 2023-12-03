from datetime import timedelta, datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.urls import path

from .models import Turma, Aluno, Frequencia, Curso, Professor, Assign, AssignTime, FrequenciaTurma
from .models import CursoAluno, Pontuacao, User, AttendanceRange


days = {
    'Segunda': 1,
    'Terça': 2,
    'Quarta': 3,
    'Quinta': 4,
    'Sexta': 5,
    'Sábado': 6,
}


def daterange(data_inicio, data_fim):
    for n in range(int((data_fim - data_inicio).days)):
        yield data_inicio + timedelta(n)


class TurmaInline(admin.TabularInline):
    model = Turma
    extra = 0


class AlunoInline(admin.TabularInline):
    model = Aluno
    extra = 0


class TurmaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nivel')
    search_fields = ('id', 'nivel')
    ordering = ['nivel']
    inlines = [AlunoInline]


class CursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('id', 'nome')
    ordering = ['id']


class AssignTimeInline(admin.TabularInline):
    model = AssignTime
    extra = 0


class AssignAdmin(admin.ModelAdmin):
    inlines = [AssignTimeInline]
    list_display = ('turma_id', 'curso', 'professor')
    search_fields = ('turma_id__id', 'nome__curso', 'nome__professor', 'curso__shortname')
    ordering = ['turma_id__id', 'curso__id']
    raw_id_fields = ['turma_id', 'curso', 'professor']


class MarksInline(admin.TabularInline):
    model = Pontuacao
    extra = 0


class CursoAlunoAdmin(admin.ModelAdmin):
    inlines = [MarksInline]
    list_display = ('aluno', 'curso',)
    search_fields = ('nome__aluno', 'nome__curso', 'aluno__turma_id__id')
    ordering = ['aluno__turma_id__id']


class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'turma_id')
    search_fields = ('nome', 'turma_id__id')
    ordering = ['turma_id__id']


class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']
    ordering = ['nome']


class FrequenciaTurmaAdmin(admin.ModelAdmin):
    list_display = ('assign', 'data', 'status')
    ordering = ['assign', 'data']
    change_list_template = 'admin/attendance_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('reset_attd/', self.reset_attd, name='reset_attd'),
        ]
        return my_urls + urls

    def reset_attd(self, request):

        data_inicio = datetime.strptime(request.POST['datainicio'], '%Y-%m-%d').date()
        data_fim = datetime.strptime(request.POST['datafinal'], '%Y-%m-%d').date()

        try:
            a = AttendanceRange.objects.all()[:1].get()
            a.data_inicio = data_inicio
            a.data_fim = data_fim
            a.save()
        except AttendanceRange.DoesNotExist:
            a = AttendanceRange(data_inicio=data_inicio, data_fim=data_fim)
            a.save()

        Frequencia.objects.all().delete()
        FrequenciaTurma.objects.all().delete()
        for asst in AssignTime.objects.all():
            for single_date in daterange(data_inicio, data_fim):
                if single_date.isoweekday() == days[asst.day]:
                    try:
                        FrequenciaTurma.objects.get(date=single_date.strftime("%Y-%m-%d"), assign=asst.assign)
                    except FrequenciaTurma.DoesNotExist:
                        a = FrequenciaTurma(date=single_date.strftime("%Y-%m-%d"), assign=asst.assign)
                        a.save()

        self.message_user(request, "Datas de frequencia excluídas com sucesso!")
        return HttpResponseRedirect("../")


admin.site.register(User, UserAdmin)
admin.site.register(Turma, TurmaAdmin)
admin.site.register(Aluno, AlunoAdmin)
admin.site.register(Curso, CursoAdmin)
admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Assign, AssignAdmin)
admin.site.register(CursoAluno, CursoAlunoAdmin)
admin.site.register(FrequenciaTurma, FrequenciaTurmaAdmin)