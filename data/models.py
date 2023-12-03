from django.db import models
import math
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete
from datetime import timedelta

sex_choice = (
    ('Masculino', 'Masculino'),
    ('Feminino', 'Feminino')
)

time_slots = (
    ('7:30 - 8:30', '7:30 - 8:30'),
    ('8:30 - 9:30', '8:30 - 9:30'),
    ('9:30 - 10:30', '9:30 - 10:30'),
    ('11:00 - 11:50', '11:00 - 11:50'),
    ('11:50 - 12:40', '11:50 - 12:40'),
    ('12:40 - 13:30', '12:40 - 13:30'),
    ('14:30 - 15:30', '14:30 - 15:30'),
    ('15:30 - 16:30', '15:30 - 16:30'),
    ('17:30 - 17:30', '16:30 - 17:30'),
)

DAYS_OF_WEEK = (
    ('Segunda', 'Segunda'),
    ('Terça', 'Terça'),
    ('Quarta', 'Quarta'),
    ('Quinta', 'Quinta'),
    ('Sexta', 'Sexta'),
    ('Sábado', 'Sábado'),
)

nome_teste = (
    ('Internal test 1', 'Internal test 1'),
    ('Internal test 2', 'Internal test 2'),
    ('Internal test 3', 'Internal test 3'),
    ('Event 1', 'Event 1'),
    ('Event 2', 'Event 2'),
    ('Semester End Exam', 'Semester End Exam'),
)

class User(AbstractUser):
    @property
    def se_aluno(self):
        if hasattr(self, 'aluno'):
            return True
        return False

    @property
    def se_professor(self):
        if hasattr(self, 'professor'):
            return True
        return False

class Curso(models.Model):
    id = models.CharField(primary_key='True', max_length=50)
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome
    
class Turma(models.Model):
    id = models.CharField(primary_key='True', max_length=100)
    nivel = models.IntegerField()

    class Meta:
        verbose_name_plural = 'turmas'

    def __str__(self):
        return '%d' % (self.nivel)
    
class Aluno(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    turma_id = models.ForeignKey(Turma, on_delete=models.CASCADE, default=1)
    nome = models.CharField(max_length=200)
    sexo = models.CharField(max_length=50, choices=sex_choice, default='Feminino')
    nascimento = models.DateField(default='01-01-1998')

    def __str__(self):
        return self.name
    
class Professor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    id = models.CharField(primary_key=True, max_length=100)
    nome = models.CharField(max_length=100)
    sexo = models.CharField(max_length=50, choices=sex_choice, default='Male')
    nascimento = models.DateField(default='01-01-1998')

    def __str__(self):
        return self.name

class Assign(models.Model):
    turma_id = models.ForeignKey(Turma, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('curso', 'turma_id', 'professor'),)
        verbose_name = 'Associação'
        verbose_name_plural = 'Associações'

    def __str__(self):
        tr = Turma.objects.get(id=self.turma_id_id)
        cr = Curso.objects.get(id=self.curso_id)
        pr = Professor.objects.get(id=self.professor_id)
        return '%s : %s : %s' % (pr.name, cr.shortname, tr)


class AssignTime(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    periodo = models.CharField(max_length=50, choices=time_slots, default='11:00 - 11:50')
    dia = models.CharField(max_length=15, choices=DAYS_OF_WEEK)

class FrequenciaTurma(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    data = models.DateField()
    status = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Frequência'
        verbose_name_plural = 'Frequências'


class Frequencia(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    frequenciaturma = models.ForeignKey(FrequenciaTurma, on_delete=models.CASCADE, default=1)
    data = models.DateField(default='01-10-2000')
    status = models.BooleanField(default='True')

    def __str__(self):
        nomealuno = Aluno.objects.get(name=self.aluno)
        nomecurso = Curso.objects.get(name=self.curso)
        return '%s : %s' % (nomealuno.name, nomecurso.shortname)


class FrequenciaTotal(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)

    #ordenação
    class Meta:
        unique_together = (('aluno', 'curso'),)
    
    @property
    def att_class(self):
        al= Aluno.objects.get(name=self.aluno)
        cr = Curso.objects.get(name=self.curso)
        att_class = Frequencia.objects.filter(curso=cr, aluno=al, status='True').count()
        return att_class

    @property
    def qtdturma(self):
        al = Aluno.objects.get(name=self.aluno)
        cr = Curso.objects.get(name=self.curso)
        qtdturma = Frequencia.objects.filter(curso=cr, aluno=al).count()
        return qtdturma

    @property
    def frequencia(self):
        al = Aluno.objects.get(name=self.aluno)
        cr = Curso.objects.get(name=self.curso)
        qtdturma = Frequencia.objects.filter(curso=cr, aluno=al).count()
        att_class = Frequencia.objects.filter(curso=cr, aluno=al, status='True').count()
        if qtdturma == 0:
            frequencia = 0
        else:
            frequencia = round(att_class / qtdturma * 100, 2)
        return frequencia

    @property
    def total_aulas(self):
        al = Aluno.objects.get(name=self.aluno)
        cr = Curso.objects.get(name=self.curso)
        qtdturma = Frequencia.objects.filter(curso=cr, aluno=al).count()
        att_class = Frequencia.objects.filter(curso=cr, aluno=al, status='True').count()
        #cálculo do total de aulas para assistir
        ta = math.ceil((0.75 * qtdturma - att_class) / 0.25)
        if ta < 0:
            return 0
        return ta
    
class CursoAluno(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('aluno', 'curso'),)
        verbose_name_plural = 'Pontuações'

    def __str__(self):
        nomealuno = Aluno.objects.get(name=self.aluno)
        nomecurso = Curso.objects.get(name=self.curso)
        return '%s : %s' % (nomealuno.name, nomecurso.shortname)

    def get_cie(self):
        pontuacao_list = self.pontuacao_set.all()
        m = []
        for mk in pontuacao_list:
            m.append(mk.pontuacao1)
        cie = math.ceil(sum(m[:5]) / 2)
        return cie

    def get_attendance(self):
        a = FrequenciaTotal.objects.get(aluno=self.aluno, curso=self.curso)
        return a.frequencia
    
class Pontuacao(models.Model):
    cursoaluno = models.ForeignKey(CursoAluno, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50, choices=nome_teste, default='Internal test 1')
    pontuacao1 = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        unique_together = (('cursoaluno', 'nome'),)

    @property
    def total_pontuacao(self):
        if self.nome == 'Semester End Exam':
            return 100
        return 20    
    
class PontuacaoTurma(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50, choices=nome_teste, default='Internal test 1')
    status = models.BooleanField(default='False')

    class Meta:
        unique_together = (('assign', 'nome'),)

    @property
    def total_pontuacao(self):
        if self.nome == 'Semester End Exam':
            return 100
        return 20


class AttendanceRange(models.Model):
    data_inicio = models.DateField()
    data_fim = models.DateField()


# Triggers


def daterange(data_inicio, data_fim):
    for n in range(int((data_fim - data_inicio).days)):
        yield data_inicio + timedelta(n)

days = {
    'Segunda': 1,
    'Terça': 2,
    'Quarta': 3,
    'Quinta': 4,
    'Sexta': 5,
    'Sábado': 6,
}

def criar_frequencia(sender, instance, **kwargs):
    if kwargs['criado']:
        data_inicio = AttendanceRange.objects.all()[:1].get().data_inicio
        data_fim = AttendanceRange.objects.all()[:1].get().data_fim
        for single_date in daterange(data_inicio, data_fim):
            if single_date.isoweekday() == days[instance.day]:
                try:
                    FrequenciaTurma.objects.get(date=single_date.strftime("%Y-%m-%d"), assign=instance.assign)
                except FrequenciaTurma.DoesNotExist:
                    a = FrequenciaTurma(date=single_date.strftime("%Y-%m-%d"), assign=instance.assign)
                    a.save()

def criar_pontuacao(sender, instance, **kwargs):
    if kwargs['criado']:
        if hasattr(instance, 'nome'):
            ass_list = instance.class_id.assign_set.all()
            for ass in ass_list:
                try:
                    CursoAluno.objects.get(aluno=instance, curso=ass.curso)
                except CursoAluno.DoesNotExist:
                    sc = CursoAluno(aluno=instance, curso=ass.curso)
                    sc.save()
                    sc.pontuacao_set.create(name='Internal test 1')
                    sc.pontuacao_set.create(name='Internal test 2')
                    sc.pontuacao_set.create(name='Internal test 3')
                    sc.pontuacao_set.create(name='Event 1')
                    sc.pontuacao_set.create(name='Event 2')
                    sc.pontuacao_set.create(name='Semester End Exam')
        elif hasattr(instance, 'curso'):
            stud_list = instance.class_id.aluno_set.all()
            cr = instance.curso
            for s in stud_list:
                try:
                    CursoAluno.objects.get(aluno=s, curso=cr)
                except CursoAluno.DoesNotExist:
                    sc = CursoAluno(aluno=s, curso=cr)
                    sc.save()
                    sc.pontuacao_set.create(name='Internal test 1')
                    sc.pontuacao_set.create(name='Internal test 2')
                    sc.pontuacao_set.create(name='Internal test 3')
                    sc.pontuacao_set.create(name='Event 1')
                    sc.pontuacao_set.create(name='Event 2')
                    sc.pontuacao_set.create(name='Semester End Exam')


def criar_pontuacao_turma(sender, instance, **kwargs):
    if kwargs['criado']:
        for nome in nome_teste:
            try:
                PontuacaoTurma.objects.get(assign=instance, name=nome[0])
            except PontuacaoTurma.DoesNotExist:
                m = PontuacaoTurma(assign=instance, name=nome[0])
                m.save()

def deletar_pontuacao(sender, instance, **kwargs):
    stud_list = instance.class_id.aluno_set.all()
    CursoAluno.objects.filter(curso=instance.curso, aluno__in=stud_list).delete()

post_save.connect(criar_pontuacao, sender=Aluno)
post_save.connect(criar_pontuacao, sender=Assign)
post_save.connect(criar_pontuacao_turma, sender=Assign)
post_save.connect(criar_frequencia, sender=AssignTime)
post_delete.connect(deletar_pontuacao, sender=Assign)