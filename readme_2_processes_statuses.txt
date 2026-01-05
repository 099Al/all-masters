/profile src/handlers/menu/commands.py
берет данные из таблицы specialists
Не показывает работы
Там же определяется путь к фото  photo_location\photo_name   (images/avatars)
Показывает Collage данных, до модерации


При редактировании. После подтверждения
сразу не меняются фото.
При выборе /profile  будет новое фото из из ModerateData (new_avatars)
При выборе Я Мастер  будет из SpecialistPhoto (collage)
При этом в new_collage сформирован новый коллаж




/start - src/handlers/menu/start/start.py
  я мастер - ведет к регистации dialog_manager.start(CheckinDialog.checkin_message)
   или к карточке существующего мастера  specialist_registration
      dialog_manager.start(CheckinDialog.info_message, data=user_data) ->  src/handlers/checkin/info_window.py
      Берем специалиста из specialists
      если статус NEW, то берем фото из ModerateSpecialistPhoto(moderate_specialist_photos) с типом COLLAGE   new_collage, new_works
      если статус APPROVED, то берем из SpecialistPhoto(specialist_photos) с типом COLLAGE                    collage, works







Specialist (status,  result_status)
result_status заполняется на основе status из ModerateStatus
status result_status  moderatedata.status

1--
NEW  NULL   NEW(далее может быть APPROVED, REJECTED, BANNED, DELETED)
Новый пользователь. На модерации. Показываем из Specialist
2--
NEW  NEW_CHANGES  NEW_CHANGES
Новый пользователь. Сделал изменения до одобрения. Показываем из ModerateData
В ModerateDate может быть REJECTED, BANNED, DELETED, BANNED, т.е не успели обновиться в Specialist
Пользователь еще может обновить данные. И отправить на повторную модерацию
3--
NEW  DELAY   NEW_CHANGES (или далее REJECTED, BANNED, DELETED)
Пользователь слишком часто делал изменения. Показываем из ModerateData.
Кнопка внести изменения не доступна.
Статус меняется через час
Далее переходит в NEW NEW_CHANGES  NEW_CHANGES
4--
NEW  REJECTED  REJECTED( далее X(удалена))
Пользователь не прошел модерацию. Показываем из Specialist
Показываем причину отказа.
В ModerateData запись может отсутствовать
Далее переходит в NEW NEW_CHANGES  NEW_CHANGES
5--
APPROVED APPROVED  APPROVED (далее X(удалена))
Пользователь одобрен. Показываем из Specialist
6--
APPROVED NEW_CHANGES  NEW_CHANGES
Пользователь обновил данные. Показываем из ModerateData
Пользователь еще может обновить данные. И отпрпавить на повторную модерацию
7--
APPROVED DELAY   NEW_CHANGES (или далее REJECTED, BANNED, DELETED)
Пользователь слишком часто делал изменения. Показываем из ModerateData.
Кнопка внести изменения не доступна.
Статус меняется через час
8--
APPROVED REJECTED  REJECTED( далее X(удалена))
Пользователь открыт. Но новый изменения не прошли модерацию. Показываем из Specialist
Показываем причину отказа.
В ModerateData запись может отсутствовать
Далее переходит в APPROVED NEW_CHANGES  NEW_CHANGES



После попадания в ModerateData
По данным в speciality и about определяется вид деятельности специалиста,
через api-gpt.  После устанавливается флаг applied_category = True


В Specialist ереносятся данные из ModerateData, если status=APPROVED, applied_category=True



