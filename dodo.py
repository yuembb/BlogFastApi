from django.utils.text import slugify

from base_engine import create_db_session

print(slugify("Windows 2008 nasıl kurulur."))




den = [{'id': 4, 'content': {'name': 'Spor', 'slug': 'spor'}}, {'id': 5, 'content': {'name': 'Sanat', 'slug': 'sanat'}}, {'id': 6, 'content': {'name': 'Yemek', 'slug': 'yemek'}}, {'id': 7, 'content': {'name': 'Gezi', 'slug': 'gezi'}}, {'id': 8, 'content': {'name': 'Game', 'slug': 'game'}}, {'id': 2, 'content': {'name': 'Sağlık', 'slug': 'saglk'}}, {'id': 1, 'content': {'name': 'Teknoloji', 'slug': 'teknoloji'}}, {'id': 12, 'content': {'name': 'Eğlence Sektörü', 'slug': 'eglence-sektoru'}}, {'id': 3, 'content': {'name': 'Eğitim', 'slug': 'egitim'}}]