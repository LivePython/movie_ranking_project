import requests


# title = input('Enter the movie title: ')
# url = f"https://api.themoviedb.org/3/search/movie"
# parameters = {
#     'api_key': 'cb3667269fb6fbf10bc31d163e2cc571',
#     'query': title
# }
# movie_data = []
# response = requests.get(url=url, params=parameters)
# data = response.json()['results']
#
# print(data)

# id= '19995, 111332, 76600, 183392, 183392'

movie_id = 19995
image_url = 'https://image.tmdb.org/t/p/'
url = f"https://api.themoviedb.org/3/movie/{movie_id}"
parameters = {
    'api_key': 'cb3667269fb6fbf10bc31d163e2cc571',
    "language": "en-US"
}
response = requests.get(url=url, params=parameters)
data = response.json()

print(data['original_title'])
print(data['release_date'].split('-')[0])
print(data['overview'])
print(f'{image_url}{data["poster_path"]}')