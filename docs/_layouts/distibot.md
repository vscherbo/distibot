{% capture md %}
* [Главная]({{site.url}}/{{site.project}}/index.html "Главная")
* [Алгоритм]({{site.url}}/{{site.project}}/rules/index.html "Алгоритм работы")
* [Компоненты]({{site.url}}/{{site.project}}/components/index.html "Компоненты дистибота")
* [История]({{site.url}}/{{site.project}}/history/index.html "История создания")
* [Галерея]({{site.url}}/{{site.project}}/gallery/index.html "Галерея")
* [Контакты]({{site.url}}/{{site.project}}/contacts/index.html "Контакты")
# {{page.title}}
{% endcapture %}
{{ md | markdownify }}
---
layout: default
---
{{ content }}