---
title: История создания дистибота
layout: default
description: Этапы создания робота дистиллятора
keywords: автоматика,дистилляция,брага,самогон,дробная перегонка,автоматизация
---
История

Первая версия управляла с аппаратом Мини МХ. Сначала робот был собран на [универсальной макетной плате]({{site.url}}/{{site.project}}/galery/distibot_on_breadboard-20160613_173816-ts1512672061.jpg "Первая проба")

После обкатки алгоритмов аппаратная часть робота была перенесена на [специализированную макетную плату]({{site.url}}/{{site.project}}/galery/distibot_1st_release-20170122_201133-ts1512672060.jpg "Дистибот на макетной плате") для Raspberry Pi, элементы к которой были уже припаяны.

Был создан [датчик голов]({{site.url}}/{{site.project}}/galery/distibot_heads_sensor-20170218_180512-ts1512672060.jpg "датчик голов"),  основанный на замыкании дистиллятом двух проводников.

Используется три проводника: один общий и два сигнальных для фиксации моментов:
* начала отбора голов
* достижения заданного уровня голов в ёмкости, что служит сигналом к переключению на отбор тела.

Для разделения фракций дробной перегонки используются два [трёхходовых соленоидных клапана]({{site.url}}/{{site.project}}/galery/distibot-3way-valve-20160613_173816-ts1512672060.jpg "Трёхходовые соленоидные клапаны")

[Первая версия]({{site.url}}/{{site.project}}/galery/distibot_on_prototyping_board-20161120_183635-ts1512672061.jpg "Первая версия дистибота") дистилляционного робота в сборе.

За процессом можно следить на экране своего смартфона, планшета или ПК, зайдя на встроенный [веб-сайт]({{site.url}}/{{site.project}}/galery/screenshot_2017-02-18-19-49-25-ts1512591128.png "Скриншот веб-сайта дистибота")

Протокол работы робот записывает в протокол (csv файл), который легко конвертировать в [график](https://docs.google.com/spreadsheets/d/e/2PACX-1vQKVkhn2IV3O2DWPfm31xbuuNPdL8AR2d5d1wyDTlDyx5drlEgdRp8TZ8kN6Dnzw809yDsPuS1UphSW/pubchart?oid=1961167213&amp;format=interactive "График на Google Docs")

Вторая версия в стадии пуско-наладки. Среди новшеств:
* включение охлаждения автоматически при достижения заданного температурного порога
* датчик потока воды на выходе системы охлаждения для экстренной остановки процесса, если с охлаждением что-то не так
* контроль температуры как в кубе, так и на входе холодильника
* автоматический сброс содержимого сухопарника
* [оптический датчик голов]({{site.url}}/{{site.project}}/galery/distibot_heads_optical_sensor-01-ts1514999010.jpg "оптический датчик голов")