# async_architecture
repository for async architecture course


Сделала Oauth через django-oauth-toolkit

Логин осуществляется через ручку accounts/login, там есть кнопка login with oauth, которая редиректит пользователя в AuthLoginView, внутри которой осуществялется логика Oauth. После того, как access token из oauth сервиса прилетает в AuthCallbackView, его можно добавить в хедеры реквестов к Task Tracker сервису. При первом запросе к сервису, тк в сервисе таск трекера не находится токена, сервис идёт в Auth сервис в ручку introspect/ для валидации токена и дальнейшего его создания в сервисе таск-трекинга.

Работа с кафкой реализована через kafka-python. Чтение событий производится внутри команды consume_events.