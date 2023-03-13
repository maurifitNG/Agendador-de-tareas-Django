from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# Create your views here.
# vista home


def home(request):
    return render(request, 'home.html')


# vista registrarse
def signup(request):
    # si la solicitud es del tipo GET, muestra el formulario de registro
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm  # formulario de registro
        })
    # si la solicitud no es del tipo GET, procesa el formulario de registro
    else:
        # verifica si las contraseñas proporcionadas por el usuario coinciden
        if request.POST['password1'] == request.POST['password2']:
            # si las contraseñas coinciden, intenta registrar al usuario
            try:
                # crea un usuario con el nombre de usuario y contraseña proporcionados
                user = User.objects.create_user(username=request.POST['username'],
                                                password=request.POST['password1'])
                # guarda el usuario en la base de datos
                user.save()
                # inicia sesión en el sitio web con el nuevo usuario
                login(request, user)
                # redirige al usuario a la página de tareas
                return redirect('tasks')
            # si el nombre de usuario ya existe, muestra un mensaje de error
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,  # formulario de registro
                    'error': 'El nombre de usuario ya existe'  # mensaje de error
                })
        # si las contraseñas no coinciden, muestra un mensaje de error
        return render(request, 'signup.html', {
            'form': UserCreationForm,  # formulario de registro
            'error': 'la contraseña no coincide'  # mensaje de error
        })


@login_required
def tasks(request):
    # Selecciona todas las tareas que pertenecen al usuario actual y que aún no se han completado
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    # Renderiza la plantilla "tasks.html" y pasa las tareas como contexto
    return render(request, 'tasks.html', {'tasks': tasks})


@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {'tasks': tasks})


@login_required
def create_task(request):
    # si la solicitud es del tipo GET, muestra el formulario para crear una nueva tarea
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm  # formulario para crear una nueva tarea
        })
    # si la solicitud no es del tipo GET, procesa el formulario para crear una nueva tarea
    else:
        try:
            # crea una instancia del formulario de creación de tarea con los datos enviados en la solicitud POST
            form = TaskForm(request.POST)
            # crea una nueva tarea utilizando los datos del formulario
            new_task = form.save(commit=False)
            # establece el usuario actual como el propietario de la tarea
            new_task.user = request.user
            # guarda la tarea en la base de datos
            new_task.save()
            # redirige al usuario a la página de tareas
            return redirect('tasks')
        # si los datos enviados en el formulario no son válidos, muestra un mensaje de error
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,  # formulario para crear una nueva tarea
                'error': 'por favor entregue datos validos'  # mensaje de error
            })


@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        # Obtener la tarea con el id proporcionado o mostrar un error 404 si no existe
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        # Crear un formulario para la tarea y rellenarlo con los datos actuales de la tarea
        form = TaskForm(instance=task)
        # Renderizar la plantilla "task_detail.html" y pasar la tarea y el formulario como contexto
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': "Error al actualizar la tarea"}) 


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user= request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user= request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')


@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    # si la solicitud es del tipo GET, muestra el formulario de inicio de sesión
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm  # formulario de inicio de sesión
        })
    # si la solicitud no es del tipo GET, procesa los datos del formulario de inicio de sesión
    else:
        # autentica al usuario utilizando el nombre de usuario y la contraseña proporcionados en la solicitud POST
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        # si las credenciales no son válidas, muestra un mensaje de error
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,  # formulario de inicio de sesión
                'error': 'usuario o contraseña incorrecto'  # mensaje de error
            })
        # si las credenciales son válidas, inicia sesión y redirige al usuario a la página de tareas
        else:
            login(request, user)  # inicia sesión en el sistema
            return redirect('tasks')  # redirige al usuario a la página de tareas

