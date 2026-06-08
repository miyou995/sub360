from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.clients.models import ClientProfile
from apps.companies.models import Company
from apps.documents.models import DocumentKind, DocumentStatus, ProofDocument
from apps.subcontractors.models import Subcontractor
from apps.subscriptions.models import Subscription, SubscriptionStatus
from apps.users.models import User

pytestmark = pytest.mark.django_db

LIST_URL = reverse("subcontractors:list_subcontractor")


def make_subcontractor(name, *, sub_status=SubscriptionStatus.ACTIVE):
    company = Company.objects.create(name=name)
    sub = Subcontractor.objects.create(company=company, location=name)
    Subscription.objects.create(subcontractor=sub, package="basic", status=sub_status)
    return sub


def add_insurance(sub, *, status, valid_until):
    return ProofDocument.objects.create(
        subcontractor=sub,
        kind=DocumentKind.INSURANCE,
        status=status,
        valid_until=valid_until,
        file="proof_documents/x.pdf",
    )


@pytest.fixture
def client_user():
    user = User.objects.create_user(email="client@example.com", password="pwd12345")
    ClientProfile.objects.create(
        user=user, company=Company.objects.create(name="Client SA")
    )
    return user


def test_anonymous_redirected(client):
    response = client.get(LIST_URL)
    assert response.status_code in (302, 403)


def test_subcontractor_only_user_forbidden(client):
    user = User.objects.create_user(email="sub@example.com", password="pwd12345")
    client.force_login(user)
    response = client.get(LIST_URL)
    assert response.status_code == 403


def test_client_user_sees_list(client, client_user):
    make_subcontractor("Alpha")
    client.force_login(client_user)
    response = client.get(LIST_URL)
    assert response.status_code == 200
    assert b"Alpha" in response.content


def test_only_active_subscriptions_listed(client, client_user):
    make_subcontractor("Active Co", sub_status=SubscriptionStatus.ACTIVE)
    make_subcontractor("Canceled Co", sub_status=SubscriptionStatus.CANCELED)
    client.force_login(client_user)
    response = client.get(LIST_URL)
    assert b"Active Co" in response.content
    assert b"Canceled Co" not in response.content


def test_insurance_annotation_valid_and_invalid(client, client_user):
    future = timezone.now().date() + timedelta(days=30)
    past = timezone.now().date() - timedelta(days=1)

    valid_sub = make_subcontractor("Valid Co")
    add_insurance(valid_sub, status=DocumentStatus.VALID, valid_until=future)

    expired_sub = make_subcontractor("Expired Co")
    add_insurance(expired_sub, status=DocumentStatus.VALID, valid_until=past)

    review_sub = make_subcontractor("Review Co")
    add_insurance(review_sub, status=DocumentStatus.REVIEW, valid_until=future)

    none_sub = make_subcontractor("None Co")  # noqa: F841

    client.force_login(client_user)
    qs = client.get(LIST_URL).context["object_list"]
    by_name = {s.company.name: s.has_valid_insurance for s in qs}

    assert by_name["Valid Co"] is True
    assert by_name["Expired Co"] is False
    assert by_name["Review Co"] is False
    assert by_name["None Co"] is False


def test_insurance_filter_true(client, client_user):
    future = timezone.now().date() + timedelta(days=30)
    valid_sub = make_subcontractor("Insured Co")
    add_insurance(valid_sub, status=DocumentStatus.VALID, valid_until=future)
    make_subcontractor("Uninsured Co")

    client.force_login(client_user)
    response = client.get(LIST_URL, {"has_valid_insurance": "true"})
    assert b"Insured Co" in response.content
    assert b"Uninsured Co" not in response.content


def test_search_filter(client, client_user):
    make_subcontractor("Zurich Builders")
    make_subcontractor("Geneva Works")

    client.force_login(client_user)
    response = client.get(LIST_URL, {"search": "Zurich"})
    assert b"Zurich Builders" in response.content
    assert b"Geneva Works" not in response.content
