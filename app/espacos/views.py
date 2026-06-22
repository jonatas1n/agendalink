from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from agendamentos.models import Appointment
from billing.decorators import require_store_subscription
from produtos.models import Product
from .forms import SpaceForm
from .models import Space, SpaceMember


def public_space(request, slug):
    space = get_object_or_404(Space, slug=slug, active=True)
    members = space.members.filter(status="ativo").select_related("user")
    return render(
        request,
        "espacos/publico.html",
        {
            "space": space,
            "members": members,
        },
    )


def public_professional(request, slug, member_id):
    space = get_object_or_404(Space, slug=slug, active=True)
    member = get_object_or_404(SpaceMember, pk=member_id, space=space, status="ativo")
    products = Product.objects.filter(owner=member.user, space=space, active=True)
    return render(
        request,
        "espacos/profissional.html",
        {
            "space": space,
            "member": member,
            "products": products,
        },
    )


def book_conversation(request, slug, product_id):
    space = get_object_or_404(Space, slug=slug, active=True)
    product = get_object_or_404(Product, pk=product_id, space=space, active=True)
    member = get_object_or_404(
        SpaceMember,
        user=product.owner,
        space=space,
        status="ativo",
    )
    user = request.user
    return render(
        request,
        "espacos/agendar_conversa.html",
        {
            "space": space,
            "product": product,
            "member": member,
            "logged_in_user": user if user.is_authenticated else None,
        },
    )


@login_required
@require_store_subscription
def create_space(request):
    if request.method == "POST":
        form = SpaceForm(request.POST, request.FILES)
        if form.is_valid():
            space = form.save(commit=False)
            space.admin = request.user
            space.save()
            SpaceMember.objects.create(
                space=space,
                user=request.user,
                role="admin",
                status="ativo",
            )
            messages.success(request, f'Espaço "{space.name}" criado!')
            return redirect("edit_space", slug=space.slug)
    else:
        form = SpaceForm()
    return render(
        request, "espacos/form_espaco.html", {"form": form, "title": "Criar espaço"}
    )


@login_required
@require_store_subscription
def edit_space(request, slug):
    space = get_object_or_404(Space, slug=slug, admin=request.user)
    if request.method == "POST":
        form = SpaceForm(request.POST, request.FILES, instance=space)
        if form.is_valid():
            form.save()
            messages.success(request, "Espaço atualizado!")
            return redirect("edit_space", slug=space.slug)
    else:
        form = SpaceForm(instance=space)
    return render(
        request,
        "espacos/form_espaco.html",
        {
            "form": form,
            "title": "Editar espaço",
            "space": space,
        },
    )


@login_required
@require_store_subscription
def manage_members(request, slug):
    space = get_object_or_404(Space, slug=slug, admin=request.user)
    members = space.members.select_related("user").all()

    if request.method == "POST":
        action = request.POST.get("action")
        member_id = request.POST.get("member_id")

        if action == "convidar":
            from django.contrib.auth.models import User

            email = request.POST.get("email", "").strip()
            try:
                user = User.objects.get(email=email)
                _, created = SpaceMember.objects.get_or_create(
                    space=space,
                    user=user,
                    defaults={"status": "ativo", "role": "membro"},
                )
                if created:
                    messages.success(
                        request,
                        f"{user.get_full_name() or user.username} adicionado ao espaço.",
                    )
                else:
                    messages.info(request, "Usuário já é membro.")
            except User.DoesNotExist:
                messages.error(
                    request, "Nenhum usuário com esse e-mail foi encontrado."
                )

        elif action == "remover" and member_id:
            SpaceMember.objects.filter(pk=member_id, space=space).exclude(
                user=request.user
            ).update(status="inativo")
            messages.success(request, "Membro removido.")

        elif action == "toggle_agenda":
            space.collective_schedule_active = not space.collective_schedule_active
            space.save()
            state = "ativada" if space.collective_schedule_active else "desativada"
            messages.success(request, f"Agenda coletiva {state}.")

        return redirect("manage_members", slug=slug)

    return render(
        request,
        "espacos/membros.html",
        {
            "space": space,
            "members": members,
        },
    )


@login_required
def collective_schedule(request, slug):
    space = get_object_or_404(Space, slug=slug, active=True)

    try:
        member = SpaceMember.objects.get(space=space, user=request.user, status="ativo")
    except SpaceMember.DoesNotExist:
        messages.error(request, "Você não é membro deste espaço.")
        return redirect("public_space", slug=slug)

    if not space.collective_schedule_active:
        messages.info(
            request,
            "A agenda coletiva não está habilitada pelo administrador do espaço.",
        )
        return redirect("public_space", slug=slug)

    member_user_ids = space.members.filter(status="ativo").values_list(
        "user_id", flat=True
    )
    appointments = (
        Appointment.objects.filter(
            product__space=space,
            product__owner_id__in=member_user_ids,
            status__in=["confirmado", "pendente"],
        )
        .select_related("product", "product__owner", "customer")
        .order_by("starts_at")
    )

    return render(
        request,
        "espacos/agenda_coletiva.html",
        {
            "space": space,
            "appointments": appointments,
            "current_member": member,
        },
    )
