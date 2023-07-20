import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import community_token, access_token
from core import VkTools
from data_store import update_user, get_user_by_id, create_user, get_view, create_view


class BotInterface:
    def __init__(self, community_token, access_token):
        self.interface = vk_api.VkApi(token=community_token)
        self.api = VkTools(token=access_token)
        self.owner_info = None

    def message_send(self, user_id, message=None, attachment=None):
        self.interface.method(
            method='messages.send',
            values={
                'user_id': user_id,
                'message': message,
                'random_id': get_random_id(),
                'attachment': attachment
            }
        )

    def event_handler(self):
        long_pull = VkLongPoll(self.interface)
        user_in_db = None
        found_users = None
        for event in long_pull.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    if not self.owner_info:
                        self.owner_info = self.api.get_profile_info(event.user_id)
                    user_in_db = get_user_by_id(user_id=self.owner_info['id'])
                    if not user_in_db:
                        user_in_db = create_user(
                            user_id=self.owner_info['id'],
                        )
                    found_users = self.api.search_users(self.owner_info, offset=user_in_db.offset)
                    self.message_send(
                        user_id=event.user_id,
                        message='Добрый день! Хочешь познакомиться? Напиши "Поиск"'
            )

                elif event.text.lower() in ['М', 'Ж']:
                    self.owner_info['sex'] = 2
                    if event.text.lower() == 'М':
                        self.owner_info['sex'] = 1

                    self.message_send(
                        user_id=event.user_id,
                        message='Отлично! напиши "Поиск"'
                    )

                elif event.text.lower() == 'поиск' and user_in_db:
                    if not self.owner_info.get('sex'):
                        self.message_send(
                            user_id=event.user_id,
                            message='Укажите ваш пол: М / Ж'
                        )
                    offset = user_in_db.offset
                    if not found_users:
                        found_users = self.api.search_users(self.owner_info, offset=user_in_db.offset)

                    found_user = found_users.pop()
                    while get_view(profile_id=user_in_db.id, worksheet_id=found_user['id']):
                        found_user = self.api.search_users(self.owner_info, offset=offset)[0]
                        offset += 1
                        update_user(user_id=user_in_db.id, offset=offset)

                    if not get_view(profile_id=user_in_db.id, worksheet_id=found_user['id']):
                        create_view(
                            profile_id=user_in_db.id, worksheet_id=found_user['id']
                        )

                    photos_user = self.api.get_photos(found_user['id'])
                    attachment = ''
                    for photo in photos_user[:3]:
                        attachment += f'photo{found_user["id"]}_{photo["id"]},'

                    self.message_send(
                        user_id=event.user_id,
                        message=f'Мне кажется,тебе подходит @id{found_user["id"]}({found_user["name"]})',
                        attachment=attachment
                    )

                elif event.text.lower() == 'Пока!':
                    self.message_send(
                        user_id=event.user_id, message='Пока!'
                    )
                else:
                    self.message_send(
                        user_id=event.user_id, message='Не понимаю, о чем ты!, Напиши Привет'
                    )


if __name__ == '__main__':
    bot = BotInterface(community_token, access_token)
    bot.event_handler()
