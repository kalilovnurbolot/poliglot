"""Site administration for admins (is_staff): user roles and blocking, activity log."""

from functools import wraps

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import url_has_allowed_host_and_scheme, urlencode, urlsafe_base64_encode
from django.views.decorators.http import require_POST

from apps.users.activity import Action, log_activity
from apps.users.models import ActivityLog, User

PAGE_SIZE = 50

# What an admin can do to a user from the users page: (fields to set, log action).
USER_ACTIONS = {
    'grant_admin': ({'is_staff': True, 'is_superuser': True}, Action.ADMIN_GRANT),
    'revoke_admin': ({'is_staff': False, 'is_superuser': False}, Action.ADMIN_REVOKE),
    'block': ({'is_active': False}, Action.USER_BLOCK),
    'unblock': ({'is_active': True}, Action.USER_UNBLOCK),
}

# Log filter groups, also used to color the entries.
ACTION_GROUPS = {
    'auth': ('Входы и регистрация', [Action.LOGIN, Action.LOGIN_GOOGLE, Action.LOGOUT, Action.REGISTER, Action.PASSWORD_RESET]),
    'failed': ('Неудачные входы', [Action.LOGIN_FAILED]),
    'content': ('Слова и грамматика', [
        Action.WORD_ADD, Action.WORD_DELETE, Action.DECK_CREATE, Action.GRAMMAR_CREATE, Action.GRAMMAR_EDIT,
        Action.GRAMMAR_DELETE, Action.GRAMMAR_LEARNED, Action.GRAMMAR_UNLEARNED,
    ]),
    'admin': ('Действия администраторов', [
        Action.ADMIN_GRANT, Action.ADMIN_REVOKE, Action.USER_BLOCK, Action.USER_UNBLOCK, Action.PASSWORD_LINK,
    ]),
}
GROUP_OF_ACTION = {action: group for group, (_, actions) in ACTION_GROUPS.items() for action in actions}


def admin_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return render(request, 'web/staff_only.html', {
                'message': 'Этот раздел доступен только администраторам.',
            }, status=403)
        return view(request, *args, **kwargs)
    return wrapper


def is_owner(user):
    """Accounts from ADMIN_EMAILS are always admins (User.save) and can't be changed here."""
    return user.email.lower() in settings.ADMIN_EMAILS


@admin_required
def users(request):
    q = request.GET.get('q', '').strip()
    role = request.GET.get('role', '')
    found = User.objects.order_by('-date_joined')
    if q:
        found = found.filter(Q(email__icontains=q) | Q(first_name__icontains=q))
    if role == 'admins':
        found = found.filter(is_staff=True)
    elif role == 'blocked':
        found = found.filter(is_active=False)
    page = Paginator(found, PAGE_SIZE).get_page(request.GET.get('page'))
    for user in page:
        user.is_owner = is_owner(user)
        user.is_me = user.pk == request.user.pk
    return render(request, 'web/manage_users.html', {
        'page': page,
        'q': q,
        'role': role,
        'search_query': urlencode({'q': q}),
        'page_query': urlencode({'q': q, 'role': role}),
        'counts': {
            'all': User.objects.count(),
            'admins': User.objects.filter(is_staff=True).count(),
            'blocked': User.objects.filter(is_active=False).count(),
        },
    })


@admin_required
@require_POST
def user_action(request, pk, action):
    target = get_object_or_404(User, pk=pk)
    if action not in USER_ACTIONS or target.pk == request.user.pk or is_owner(target):
        return render(request, 'web/staff_only.html', {
            'message': 'Это действие недоступно: нельзя менять себя и владельцев сайта.',
        }, status=403)
    fields, log_action = USER_ACTIONS[action]
    for field, value in fields.items():
        setattr(target, field, value)
    target.save(update_fields=list(fields))
    log_activity(request, log_action, target.email)
    next_url = request.POST.get('next', '')
    if url_has_allowed_host_and_scheme(next_url, {request.get_host()}, request.is_secure()):
        return redirect(next_url)
    return redirect('web:manage-users')


@admin_required
@require_POST
def user_reset_link(request, pk):
    """A one-time link the admin sends to the user (no email needed) to set a new password."""
    target = get_object_or_404(User, pk=pk)
    if target.pk == request.user.pk or is_owner(target):
        return render(request, 'web/staff_only.html', {
            'message': 'Ссылку нельзя создать для себя и для владельцев сайта.',
        }, status=403)
    path = reverse('web:password-reset', args=[urlsafe_base64_encode(force_bytes(target.pk)),
                                               default_token_generator.make_token(target)])
    log_activity(request, Action.PASSWORD_LINK, target.email)
    return render(request, 'web/manage_reset_link.html', {
        'target': target,
        'link': request.build_absolute_uri(path),
        'days': round(settings.PASSWORD_RESET_TIMEOUT / 86400),
    })


@admin_required
def activity(request):
    entries = ActivityLog.objects.select_related('user')
    user_id = request.GET.get('user', '')
    group = request.GET.get('group', '')
    q = request.GET.get('q', '').strip()
    filtered_user = None
    if user_id.isdigit():
        filtered_user = User.objects.filter(pk=user_id).first()
        entries = entries.filter(user_id=user_id)
    if group in ACTION_GROUPS:
        entries = entries.filter(action__in=ACTION_GROUPS[group][1])
    if q:
        entries = entries.filter(Q(user_email__icontains=q) | Q(target__icontains=q))
    page = Paginator(entries, PAGE_SIZE).get_page(request.GET.get('page'))
    for entry in page:
        entry.group = GROUP_OF_ACTION.get(entry.action, 'auth')
    return render(request, 'web/manage_log.html', {
        'page': page,
        'groups': [(key, label) for key, (label, _) in ACTION_GROUPS.items()],
        'group': group,
        'q': q,
        'filtered_user': filtered_user,
        'filter_query': urlencode({'user': user_id, 'q': q}),
        'page_query': urlencode({'user': user_id, 'group': group, 'q': q}),
    })
