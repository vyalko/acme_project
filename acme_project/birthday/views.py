from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy

from .forms import BirthdayForm, CongratulationForm
from .models import Birthday
from .utils import calculate_birthday_countdown
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect


@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')


# Будут обработаны POST-запросы только от залогиненных пользователей.
@login_required
def add_comment(request, pk):
    # Получаем объект дня рождения или выбрасываем 404 ошибку.
    birthday = get_object_or_404(Birthday, pk=pk)
    # Функция должна обрабатывать только POST-запросы.
    form = CongratulationForm(request.POST)
    if form.is_valid():
        # Создаём объект поздравления, но не сохраняем его в БД.
        congratulation = form.save(commit=False)
        # В поле author передаём объект автора поздравления.
        congratulation.author = request.user
        # В поле birthday передаём объект дня рождения.
        congratulation.birthday = birthday
        # Сохраняем объект в БД.
        congratulation.save()
    # Перенаправляем пользователя назад, на страницу дня рождения.
    return redirect('birthday:detail', pk=pk)


class BirthdayListView(ListView):
    model = Birthday
    queryset = Birthday.objects.prefetch_related(
        'tags'
        ).select_related('author')
    ordering = 'id'
    paginate_by = 10


#class BirthdayMixin:
#    model = Birthday
#    success_url = reverse_lazy('birthday:list')

#def delete_birthday(request, pk):
    # Получаем объект модели или выбрасываем 404 ошибку.
#    instance = get_object_or_404(Birthday, pk=pk)
    # В форму передаём только объект модели;
    # передавать в форму параметры запроса не нужно.
#    form = BirthdayForm(instance=instance)
#    context = {'form': form}
    # Если был получен POST-запрос...
#    if request.method == 'POST':
        # ...удаляем объект:
#        instance.delete()
        # ...и переадресовываем пользователя на страницу со списком записей.
#        return redirect('birthday:list')
    # Если был получен GET-запрос — отображаем форму.
#    return render(request, 'birthday/birthday.html', context)


#def birthday(request, pk=None):
    # Если в запросе указан pk (если получен запрос на редактирование объекта):
#    if pk is not None:
        # Получаем объект модели или выбрасываем 404 ошибку.
#        instance = get_object_or_404(Birthday, pk=pk)
    # Если в запросе не указан pk
    # (если получен запрос к странице создания записи):
#    else:
        # Связывать форму с объектом не нужно, установим значение None.
#        instance = None
    # Передаём в форму либо данные из запроса, либо None. 
    # В случае редактирования прикрепляем объект модели.
#    form = BirthdayForm(
#        request.POST or None,
#        files=request.FILES or None,
#        instance=instance
#    )
#    context = {'form': form}
    # Если форма валидна...
#    if form.is_valid():
#        form.save()
        # ...вызовем функцию подсчёта дней:
#        birthday_countdown = calculate_birthday_countdown(
            # ...и передаём в неё дату из словаря cleaned_data.
#            form.cleaned_data['birthday']
#        )
        # Обновляем словарь контекста: добавляем в него новый элемент.
#        context.update({'birthday_countdown': birthday_countdown})
#    return render(request, 'birthday/birthday.html', context)

#class BirthdayCreateView(CreateView):
    # Указываем модель, с которой работает CBV...
#    model = Birthday
    # Этот класс сам может создать форму на основе модели!
    # Нет необходимости отдельно создавать форму через ModelForm.
    # Указываем имя формы:
#    form_class = BirthdayForm
    # Явным образом указываем шаблон:
#    template_name = 'birthday/birthday.html'
    # Указываем namespace:name страницы, куда будет перенаправлен пользователь
    # после создания объекта:
#    success_url = reverse_lazy('birthday:list')

#def birthday_list(request):
    # Получаем список всех объектов с сортировкой по id.
#    birthdays = Birthday.objects.order_by('id')
    # Создаём объект пагинатора с количеством 5 записей на страницу.
#    paginator = Paginator(birthdays, 5)

    # Получаем из запроса значение параметра page.
#    page_number = request.GET.get('page')
    # Получаем запрошенную страницу пагинатора. 
    # Если параметра page нет в запросе или его значение не приводится к числу,
    # вернётся первая страница.
#    page_obj = paginator.get_page(page_number)
    # Вместо полного списка объектов передаём в контекст 
    # объект страницы пагинатора
#    context = {'page_obj': page_obj}
#    return render(request, 'birthday/birthday_list.html', context)
# Наследуем класс от встроенного ListView:
class BirthdayCreateView(LoginRequiredMixin, CreateView):
    model = Birthday
    form_class = BirthdayForm

    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)


class BirthdayUpdateView(LoginRequiredMixin, UpdateView):
    model = Birthday
    form_class = BirthdayForm

    def dispatch(self, request, *args, **kwargs):
        # При получении объекта не указываем автора.
        # Результат сохраняем в переменную.
        instance = get_object_or_404(Birthday, pk=kwargs['pk'])
        # Сверяем автора объекта и пользователя из запроса.
        if instance.author != request.user:
            # Здесь может быть как вызов ошибки, так и редирект на нужную страницу.
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class BirthdayDeleteView(LoginRequiredMixin, DeleteView):
    model = Birthday
    success_url = reverse_lazy('birthday:list')


class BirthdayDetailView(DetailView):
    model = Birthday

    def get_context_data(self, **kwargs):
        # Получаем словарь контекста:
        context = super().get_context_data(**kwargs)
        # Добавляем в словарь новый ключ:
        context['birthday_countdown'] = calculate_birthday_countdown(
            # Дату рождения берём из объекта в словаре context:
            self.object.birthday
        )
        # Возвращаем словарь контекста.
        # Записываем в переменную form пустой объект формы.
        context['form'] = CongratulationForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['congratulations'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.congratulations.select_related('author')
        )
        return context
