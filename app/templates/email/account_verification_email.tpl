{% extends "mail_templated/base.tpl" %}

{% block subject %}
    {{ subject }}
{% endblock %}

{% block html %}
    <p>
        Hi,
        Thank you for registering on our website.
    </p>

    <p>
        Please be so kind as to verify your email by clicking the link below:
        <a href="http://{{ domain }}/api-1.0/auth/verify/{{ token }}/">
            Verify Account
        </a>
    </p>

    <p>If it's not you, please ignore this email.</p>
{% endblock %}