import datetime
from datetime import datetime

import vk_api


class VkTools:
    def __init__(self, token):
        self.api = vk_api.VkApi(token=token)

    def get_profile_info(self, user_id):
        info = self.api.method(
            method='users.get',
            values={
                'user_id': user_id,
                'fields': ('first_name, last_name, '
                           'city, bdate, sex,relation, home_town')
            }
        )[0]

        user_info = {
            'name': f"{info['first_name']} {info['last_name']}",
            'id': info['id'],
            'bdate': info['bdate'] if 'bdate' in info else None,
            'home_town': info.get('home_town', ''),
            'sex': info.get('sex', 'пол не определён'),
            'city': info.get('city', {}).get('id', '')
        }

        return user_info

    def search_users(self, params, offset):
        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        current_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = current_year - user_year
        age_from = age - 5
        age_to = age + 5

        users = self.api.method(
            method='users.search',
            values={
                'offset': offset,
                'age_from': age_from,
                'age_to': age_to,
                'sex': sex,
                'city': city,
                'status': 6,
                'is_closed': False,
                'has_photo': True
            }).get('items', [])

        result = []
        for user in users:
            if not user['is_closed']:
                result.append({
                    'id': user['id'],
                    'name': f"{user['first_name']} {user['last_name']}",
                    'sex': sex,
                    'city': city
                })

        return result

    def get_photos(self, user_id):
        photos = self.api.method(
            method='photos.get',
            values={
                'user_id': user_id,
                'album_id': 'profile',
                'extended': 1
            }
        ).get('items', [])
        result = []
        for photo in photos:
            result.append({
                'owner_id': photo['owner_id'],
                'id': photo['id'],
                'likes': photo['likes']['count'],
                'comments': photo['comments']['count']
            })
        if result:
            result.sort(
                key=lambda x: x['likes'] + x['comments'] * 10, reverse=True
            )

        return result
