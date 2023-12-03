from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from .models import Turma, Aluno, Frequencia, Curso, Professor, Assign, FrequenciaTotal, time_slots, \
    DAYS_OF_WEEK, AssignTime, FrequenciaTurma, CursoAluno, Pontuacao, PontuacaoTurma
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def index(request): #certo na pag de templates
    if request.user.se_professor:
        return render(request, 'data/t_homepage.html')
    if request.user.se_aluno:
        return render(request, 'data/homepage.html')
    if request.user.is_superuser:
        return render(request, 'data/admin_page.html')
    return render(request, 'data/logout.html')


@login_required()
def frequencia(request, aln_id):
    aln = Aluno.objects.get(USN=aln_id)
    ass_list = Assign.objects.filter(turma_id_id=aln.turma_id)
    att_list = []
    for ass in ass_list:
        try:
            a = FrequenciaTotal.objects.get(aluno=aln, curso=ass.curso)
        except FrequenciaTotal.DoesNotExist:
            a = FrequenciaTotal(aluno=aln, curso=ass.curso)
            a.save()
        att_list.append(a)
    return render(request, 'data/frequencia.html', {'att_list': att_list})


@login_required()
def frequencia_detalhada(request, aln_id, curso_id):
    aln = get_object_or_404(Aluno, USN=aln_id)
    cr = get_object_or_404(Curso, id=curso_id)
    att_list = Frequencia.objects.filter(curso=cr, aluno=aln).order_by('date')
    return render(request, 'data/freq_detalhada.html', {'att_list': att_list, 'cr': cr})


# professor Views

@login_required
def t_clas(request, professor_id, escolha):
    professor1 = get_object_or_404(Professor, id=professor_id)
    return render(request, 'data/t_clas.html', {'professor1': professor1, 'escolha': escolha})


@login_required()
def t_aluno(request, assign_id):
    ass = Assign.objects.get(id=assign_id)
    att_list = []
    for aln in ass.turma_id.aluno_set.all():
        try:
            a = FrequenciaTotal.objects.get(aluno=aln, curso=ass.curso)
        except FrequenciaTotal.DoesNotExist:
            a = FrequenciaTotal(aluno=aln, curso=ass.curso)
            a.save()
        att_list.append(a)
    return render(request, 'data/t_alunos.html', {'att_list': att_list})


@login_required()
def t_turma_data(request, assign_id):
    now = timezone.now()
    ass = get_object_or_404(Assign, id=assign_id)
    att_list = ass.frequenciaturma_set.filter(date__lte=now).order_by('-date')
    return render(request, 'data/t_turma_data.html', {'att_list': att_list})


@login_required()
def cancela_turma(request, ass_c_id):
    assc = get_object_or_404(FrequenciaTurma, id=ass_c_id)
    assc.status = 2
    assc.save()
    return HttpResponseRedirect(reverse('t_turma_data', args=(assc.assign_id,)))


@login_required()
def t_frequencia(request, ass_c_id):
    assc = get_object_or_404(FrequenciaTurma, id=ass_c_id)
    ass = assc.assign
    c = ass.turma_id
    context = {
        'ass': ass,
        'c': c,
        'assc': assc,
    }
    return render(request, 'data/t_frequencia.html', context)


@login_required()
def editar_att(request, ass_c_id):
    assc = get_object_or_404(FrequenciaTurma, id=ass_c_id)
    cr = assc.assign.curso
    att_list = Frequencia.objects.filter(frequenciaturma=assc, curso=cr)
    context = {
        'assc': assc,
        'att_list': att_list,
    }
    return render(request, 'data/t_editar_att.html', context)


@login_required()
def confirm(request, ass_c_id):
    assc = get_object_or_404(FrequenciaTurma, id=ass_c_id)
    ass = assc.assign
    cr = ass.curso
    cl = ass.turma_id
    for i, s in enumerate(cl.aluno_set.all()):
        status = request.POST[s.USN]
        if status == 'presente':
            status = 'True'
        else:
            status = 'False'
        if assc.status == 1:
            try:
                a = Frequencia.objects.get(curso=cr, aluno=s, data=assc.data, frequenciaturma=assc)
                a.status = status
                a.save()
            except Frequencia.DoesNotExist:
                a = Frequencia(curso=cr, aluno=s, status=status, data=assc.data, frequenciaturma=assc)
                a.save()
        else:
            a = Frequencia(curso=cr, aluno=s, status=status, data=assc.data, frequenciaturma=assc)
            a.save()
            assc.status = 1
            assc.save()

    return HttpResponseRedirect(reverse('t_turma_data', args=(ass.id,)))


@login_required()
def t_frequencia_detalhada(request, aln_id, curso_id):
    aln = get_object_or_404(Aluno, USN=aln_id)
    cr = get_object_or_404(Curso, id=curso_id)
    att_list = Frequencia.objects.filter(curso=cr, aluno=aln).order_by('date')
    return render(request, 'data/t_freq_detalhada.html', {'att_list': att_list, 'cr': cr})


@login_required()
def mudar_att(request, att_id):
    a = get_object_or_404(Frequencia, id=att_id)
    a.status = not a.status
    a.save()
    return HttpResponseRedirect(reverse('t_freq_detalhada', args=(a.aluno.USN, a.curso_id)))


@login_required()
def t_extra_class(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    c = ass.turma_id
    context = {
        'ass': ass,
        'c': c,
    }
    return render(request, 'data/t_extra_class.html', context)


@login_required()
def e_confirm(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    cr = ass.curso
    cl = ass.turma_id
    assc = ass.frequenciaturma_set.create(status=1, date=request.POST['date'])
    assc.save()

    for i, s in enumerate(cl.aluno_set.all()):
        status = request.POST[s.USN]
        if status == 'present':
            status = 'True'
        else:
            status = 'False'
        date = request.POST['date']
        a = Frequencia(curso=cr, aluno=s, status=status, date=date, Frequenciaclass=assc)
        a.save()

    return HttpResponseRedirect(reverse('t_clas', args=(ass.professor_id, 1)))


@login_required()
def t_report(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    sc_list = []
    for aln in ass.turma_id.aluno_set.all():
        a = CursoAluno.objects.get(aluno=aln, curso=ass.curso)
        sc_list.append(a)
    return render(request, 'data/t_report.html', {'sc_list': sc_list})


@login_required()
def timetable(request, turma_id):
    asst = AssignTime.objects.filter(assign__turma_id=turma_id)
    matrix = [['' for i in range(12)] for j in range(6)]

    for i, d in enumerate(DAYS_OF_WEEK):
        t = 0
        for j in range(12):
            if j == 0:
                matrix[i][0] = d[0]
                continue
            if j == 4 or j == 8:
                continue
            try:
                a = asst.get(period=time_slots[t][0], day=d[0])
                matrix[i][j] = a.assign.curso_id
            except AssignTime.DoesNotExist:
                pass
            t += 1

    context = {'matrix': matrix}
    return render(request, 'data/timetable.html', context)


@login_required()
def t_timetable(request, professor_id):
    asst = AssignTime.objects.filter(assign__professor_id=professor_id)
    class_matrix = [[True for i in range(12)] for j in range(6)]
    for i, d in enumerate(DAYS_OF_WEEK):
        t = 0
        for j in range(12):
            if j == 0:
                class_matrix[i][0] = d[0]
                continue
            if j == 4 or j == 8:
                continue
            try:
                a = asst.get(period=time_slots[t][0], day=d[0])
                class_matrix[i][j] = a
            except AssignTime.DoesNotExist:
                pass
            t += 1

    context = {
        'class_matrix': class_matrix,
    }
    return render(request, 'data/t_timetable.html', context)


@login_required()
def professores_livres(request, asst_id):
    asst = get_object_or_404(AssignTime, id=asst_id)
    ft_list = []
    t_list = Professor.objects.filter(assign__turma_id__id=asst.assign.turma_id_id)
    for t in t_list:
        at_list = AssignTime.objects.filter(assign__professor=t)
        if not any([True if at.period == asst.period and at.day == asst.day else False for at in at_list]):
            ft_list.append(t)

    return render(request, 'data/professores_livres.html', {'ft_list': ft_list})

# aluno pontuacao

@login_required()
def lista_pontuacao(request, aln_id):
    aln = Aluno.objects.get(USN=aln_id, )
    ass_list = Assign.objects.filter(turma_id_id=aln.turma_id)
    sc_list = []
    for ass in ass_list:
        try:
            sc = CursoAluno.objects.get(aluno=aln, curso=ass.curso)
        except CursoAluno.DoesNotExist:
            sc = CursoAluno(aluno=aln, curso=ass.curso)
            sc.save()
            sc.pontuacao_set.create(type='I', name='Internal test 1')
            sc.pontuacao_set.create(type='I', name='Internal test 2')
            sc.pontuacao_set.create(type='I', name='Internal test 3')
            sc.pontuacao_set.create(type='E', name='Event 1')
            sc.pontuacao_set.create(type='E', name='Event 2')
            sc.pontuacao_set.create(type='S', name='Semester End Exam')
        sc_list.append(sc)

    return render(request, 'data/lista_pontuacao.html', {'sc_list': sc_list})


# professor pontuacao

@login_required()
def t_lista_pontuacao(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    m_list = PontuacaoTurma.objects.filter(assign=ass)
    return render(request, 'data/t_lista_pontuacao.html', {'m_list': m_list})


@login_required()
def t_entrada_pontuacao(request, pontuacao_c_id):
    mc = get_object_or_404(PontuacaoTurma, id=pontuacao_c_id)
    ass = mc.assign
    c = ass.turma_id
    context = {
        'ass': ass,
        'c': c,
        'mc': mc,
    }
    return render(request, 'data/t_entrada_pontuacao.html', context)


@login_required()
def pontuacao_confirm(request, pontuacao_c_id):
    mc = get_object_or_404(PontuacaoTurma, id=pontuacao_c_id)
    ass = mc.assign
    cr = ass.curso
    cl = ass.turma_id
    for s in cl.aluno_set.all():
        mark = request.POST[s.USN]
        sc = CursoAluno.objects.get(curso=cr, aluno=s)
        m = sc.pontuacao_set.get(name=mc.name)
        m.pontuacao1 = mark
        m.save()
    mc.status = True
    mc.save()

    return HttpResponseRedirect(reverse('t_lista_pontuacao', args=(ass.id,)))


@login_required()
def editar_pontuacao(request, pontuacao_c_id):
    mc = get_object_or_404(PontuacaoTurma, id=pontuacao_c_id)
    cr = mc.assign.curso
    aln_list = mc.assign.turma_id.aluno_set.all()
    m_list = []
    for aln in aln_list:
        sc = CursoAluno.objects.get(curso=cr, aluno=aln)
        m = sc.pontuacao_set.get(name=mc.name)
        m_list.append(m)
    context = {
        'mc': mc,
        'm_list': m_list,
    }
    return render(request, 'data/editar_pontuacao.html', context)


@login_required()
def aluno_pontuacao(request, assign_id):
    ass = Assign.objects.get(id=assign_id)
    sc_list = CursoAluno.objects.filter(aluno__in=ass.turma_id.aluno_set.all(), curso=ass.curso)
    return render(request, 'data/t_pontuacao_aluno.html', {'sc_list': sc_list})


@login_required()
def adicionar_professor(request):
    if not request.user.is_superuser:
        return redirect("/")

    if request.method == 'POST':
        name = request.POST['full_name']
        id = request.POST['id'].lower()
        dob = request.POST['dob']
        sex = request.POST['sex']
        
        user = User.objects.create_user(
            username=name.split(" ")[0].lower() + '_' + id,
            password=name.split(" ")[0].lower() + '_' + dob.replace("-","")[:4]
        )
        user.save()

        Professor(
            user=user,
            id=id,
            name=name,
            sex=sex,
            DOB=dob
        ).save()
        return redirect('/')
    

    return render(request, 'data/add_professor.html')


@login_required()
def add_aluno(request):
    # If the user is not admin, they will be redirected to home
    if not request.user.is_superuser:
        return redirect("/")

    if request.method == 'POST':
        # Retrieving all the form data that has been inputted
        turma_id = get_object_or_404(Turma, id=request.POST['Turma'])
        name = request.POST['full_name']
        usn = request.POST['usn']
        dob = request.POST['dob']
        sex = request.POST['sex'] 

        # Creating a User with aluno username and password format
        # USERNAME: firstname + underscore + last 3 digits of USN
        # PASSWORD: firstname + underscore + year of birth(YYYY)
        user = User.objects.create_user(
            username=name.split(" ")[0].lower() + '_' + request.POST['usn'][-3:],
            password=name.split(" ")[0].lower() + '_' + dob.replace("-","")[:4]
        )
        user.save()

        # Creating a new aluno instance with given data and saving it.
        Aluno(
            user=user,
            USN=usn,
            turma_id=turma_id,
            name=name,
            sex=sex,
            DOB=dob
        ).save()
        return redirect('/')
    
    all_classes = Turma.objects.order_by('-id')
    context = {'all_classes': all_classes}
    return render(request, 'data/add_aluno.html', context)