from django.contrib import admin
from .models import AcademicGroup, Course, Department, StudentProfile
from .models import Category, Ticket


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "category",
        "status", "owner", "created_at"
    )
    list_filter = ("status", "category")
    search_fields = ("title",)


@admin.register(AcademicGroup)
class AcademicGroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'department',
    )
    list_filter = (
        'department',
    )
    search_fields = (
        'name',
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'department')
    list_filter = ('department',)
    search_fields = ('title',)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'department')
    list_filter = ('department',)
    search_fields = ('user__username',)
    filter_horizontal = ('courses',)
