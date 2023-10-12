{% extends "mail_templated/base.tpl" %}

{% block subject %}
    {{ subject }}
{% endblock %}

{% block html %}
    <p>Hi</p>

    <p>
        We're sending you this email because you requested a password reset for your user account.
        Please go to the following page and choose a new password:

        <a href="http://{{ domain }}/api-1.0/auth/password/reset/confirm/{{ token }}/">
            Reset my password
        </a>
    </p>

    <p>If you didn't request a password reset, you can ignore this email. Your password will not be changed.</p>
{% endblock %}