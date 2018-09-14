---
title: Алгоритм
layout: default
description: Отслеживаемые параметры, логика срабатывания
keywords: автоматика,дистилляция,брага,самогон,дробная перегонка,автоматизация
---
Алгоритм
Алгоритм действия дистибота станент понятен из разбора графика изменения температуры в кубе во времени.
Скриншот страницы веб-сервера дистибота. Процесс дробной перегонки браги.

Крупно выводится текущие показания датчика температуры.
Далее идёт ряд иконок, соответствующих стадиям процесса: старт, нагрев, пауза, головы, тело, хвосты, финиш. На скриншоте - сейчас идёт стадия отбора тела.
График температуры, который демонстрирует алгоритм дистибота:
Первичный нагрев. Дистибот включает индукционную плитку на максимальную мощность.
Пауза, которая обнуляет таймер автоматического отключения индукционной плитки и одновременно обеспечивает переход к медленному нагреву, необходимому для отбора голов. Дистибот выключает плитку и ...
спустя минуту включает, но уже на малой мощности. На рисунке видно, что график после резкого роста стал горизонтальным и дале его наклон значительно меньше, чем на фазе предварительного разогрева, что указывает на пониженную скорость нагрева.
При достижении температуры ожидания голов, заданной в конфигурационном файле, дистибот переводит плитку на режим самой малой мощности.
От первых капель срабатывает датчик старта голов и дистибот на веб-сервере подсвечивает иконку "головы". По достижению предварительно выставленного (расчётного) объёма голов срабатывает датчик стопа голов и
дистибот переключает клапаны так, чтобы тело направлялось в соотвествующий сосуд и одновременно увеличивает мощность плитки до средней. На скриншоте виден подъём графика температуры.
Когда датчик температуры зафиксирует 94,5 C° (задаётся в конфигурационном файле) дистибот переключит клапаны для направления хвостов в предназначенную ёмкость и увеличит мощность до максимума. Этот фрагмент на скриншоте отсутсвует.