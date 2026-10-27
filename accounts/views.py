from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from dashboards.utils import chart

from .forms import AcademicGroupForm, CourseForm, DepartmentForm
from .models import AcademicGroup, Course, Department, Category, Ticket
from .serializers import (CategorySerializer, TicketSerializer)

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

@login_required(login_url="/admin/login/")
@ensure_csrf_cookie
def dashboard(request):
    return render(request, "tickets/dashboard.html")

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Ticket.objects.filter(
            owner=self.request.user
        ).select_related("category")

        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


def is_methodist(user):
    return user.groups.filter(name='Методист').exists()


def methodist_required(view):
    return login_required(user_passes_test(is_methodist)(view))


def save_object(request, form_class, title, message, success_url, instance=None):
    form = form_class(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        messages.success(request, message)
        return redirect(success_url)
    return render(request, 'object_form.html', {'form': form, 'title': title})


def delete_object(request, obj, title, message, success_url):
    if request.method == 'POST':
        obj.delete()
        messages.success(request, message)
        return redirect(success_url)
    return render(request, 'object_confirm_delete.html', {'object': obj, 'title': title})


def filter_by_department(request, queryset):
    department = request.GET.get('department', '')
    current = int(department) if department.isdigit() else None
    if current:
        queryset = queryset.filter(department_id=current)
    return queryset, current


@login_required
def profile(request):
    departments = list(Department.objects.annotate(
        courses_n=Count('courses', distinct=True), groups_n=Count('groups', distinct=True)).order_by('pk'))
    names = [d.name for d in departments]
    return render(request, 'profile.html', {
        'is_methodist': is_methodist(request.user),
        'departments_count': len(departments),
        'groups_count': AcademicGroup.objects.count(),
        'courses_count': Course.objects.count(),
        'charts': {
            'courses': chart(names, ('Курсов', [d.courses_n for d in departments])),
            'groups': chart(names, ('Учебных групп', [d.groups_n for d in departments])),
        },
    })


@login_required
def department_list(request):
    return render(request, 'department_list.html', {
        'departments': Department.objects.annotate(
            groups_n=Count('groups', distinct=True), courses_n=Count('courses', distinct=True)),
        'is_methodist': is_methodist(request.user),
    })


@login_required
def academic_group_list(request):
    groups, current = filter_by_department(
        request, AcademicGroup.objects.select_related('department').annotate(students_n=Count('students')))
    return render(request, 'group_list.html', {
        'groups': groups,
        'departments': Department.objects.all(),
        'current_department': current,
        'is_methodist': is_methodist(request.user),
    })


@login_required
def course_list(request):
    courses, current = filter_by_department(
        request, Course.objects.select_related('department').annotate(students_n=Count('students')))
    return render(request, 'course_list.html', {
        'courses': courses,
        'departments': Department.objects.all(),
        'current_department': current,
        'is_methodist': is_methodist(request.user),
    })


@methodist_required
def department_create(request):
    return save_object(request, DepartmentForm, 'Добавление факультета', 'Факультет добавлен.', 'department_list')


@methodist_required
def department_update(request, pk):
    return save_object(request, DepartmentForm, 'Изменение факультета', 'Факультет изменён.', 'department_list',
                       get_object_or_404(Department, pk=pk))


@methodist_required
def department_delete(request, pk):
    return delete_object(request, get_object_or_404(Department, pk=pk), 'Удаление факультета',
                         'Факультет удалён.', 'department_list')


@methodist_required
def academic_group_create(request):
    return save_object(request, AcademicGroupForm, 'Добавление учебной группы', 'Группа добавлена.',
                       'academic_group_list')


@methodist_required
def academic_group_update(request, pk):
    return save_object(request, AcademicGroupForm, 'Изменение учебной группы', 'Группа изменена.',
                       'academic_group_list', get_object_or_404(AcademicGroup, pk=pk))


@methodist_required
def academic_group_delete(request, pk):
    return delete_object(request, get_object_or_404(AcademicGroup, pk=pk), 'Удаление учебной группы',
                         'Группа удалена.', 'academic_group_list')


@methodist_required
def course_create(request):
    return save_object(request, CourseForm, 'Добавление курса', 'Курс добавлен.', 'course_list')


@methodist_required
def course_update(request, pk):
    return save_object(request, CourseForm, 'Изменение курса', 'Курс изменён.', 'course_list',
                       get_object_or_404(Course, pk=pk))


@methodist_required
def course_delete(request, pk):
    return delete_object(request, get_object_or_404(Course, pk=pk), 'Удаление курса', 'Курс удалён.', 'course_list')
