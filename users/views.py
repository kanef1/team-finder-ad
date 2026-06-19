from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from users.forms import EditProfileForm, LoginForm, RegisterForm
from users.models import User


class RegisterView(View):
    def get(self, request):
        return render(request, 'users/register.html', {'form': RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
        return render(request, 'users/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('projects:list')
        return render(request, 'users/login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('projects:list')


class UserDetailView(View):
    def get(self, request, user_id):
        profile_user = get_object_or_404(User, id=user_id)
        return render(request, 'users/user-details.html', {'user': profile_user})


class UserListView(View):
    def get(self, request):
        active_filter = request.GET.get('filter', '')
        users = User.objects.all()

        if request.user.is_authenticated and active_filter:
            if active_filter == 'owners-of-favorite-projects':
                fav_projects = request.user.favorites.all()
                users = User.objects.filter(owned_projects__in=fav_projects).distinct()
            elif active_filter == 'owners-of-participating-projects':
                participating = request.user.participating_projects.all()
                users = User.objects.filter(owned_projects__in=participating).distinct()
            elif active_filter == 'interested-in-my-projects':
                my_projects = request.user.owned_projects.all()
                users = User.objects.filter(favorites__in=my_projects).distinct()
            elif active_filter == 'participants-of-my-projects':
                my_projects = request.user.owned_projects.all()
                users = User.objects.filter(participating_projects__in=my_projects).distinct()

        paginator = Paginator(users, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        query_prefix = f'filter={active_filter}&' if active_filter else ''

        return render(request, 'users/participants.html', {
            'page_obj': page_obj,
            'active_filter': active_filter,
            'query_prefix': query_prefix,
        })


class EditProfileView(LoginRequiredMixin, View):
    def get(self, request):
        form = EditProfileForm(instance=request.user)
        return render(request, 'users/edit_profile.html', {'form': form})

    def post(self, request):
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:detail', user_id=request.user.id)
        return render(request, 'users/edit_profile.html', {'form': form})


class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request):
        form = PasswordChangeForm(request.user)
        return render(request, 'users/change_password.html', {'form': form})

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('users:detail', user_id=request.user.id)
        return render(request, 'users/change_password.html', {'form': form})
