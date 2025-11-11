import requests
import json
from datetime import datetime
import pandas

#region GLOBAL CONSTANTS
AUTHORIZE_URL = 'https://osu.ppy.sh/oauth/authorize'
API_COUNTRY_RANKING_URL = 'https://osu.ppy.sh/api/v2/rankings/{0}/country?page={1}'
API_COUNTRY_PLAYER_RANKING_URL = 'https://osu.ppy.sh/api/v2/rankings/{0}/performance?country={1}&filter={2}'

#How to find own user/password: Go to your profile page on osu and then click on the pencil symbol "edit profile page". It will be on the block to the right of "joined xxx, last seen xxx, etc"
#Scroll until you find "OAuth", and then click "New OAuth Application"
#Name it whatever you want. Application Callbacks URLs are not important in this case
#You will see 'own clients', where you will click 'edit'
#Show Client secret. The Client ID is your USER. The Client secret is your PASSWORD. Copy and paste to the below variables
USER = "PLACEHOLDER"
PASSWORD = "PLACEHOLDER"

USER_ID = "PLACEHOLDER" #The player who you want to stop at when seeing who is better
#endregion


#region Classes
class Token(object):
    def __init__(self, json:json):
        self.token_type = json['token_type']
        self.token_value = json['access_token']
        

class Country(object):
    def __init__(self,json,rank:int):
        self.code = json['country']['code']
        self.name = json['country']['name']
        self.country_rank = rank

        #to fill out later when we go through each country
        self.top_country_player = None
        self.top_country_pp = None
        self.top_country_rank = None

class Player(object):
    def __init__(self,json):
        self.username = json['user']['username']
        self.id = json['user']['id']
        self.pp = json['pp']
        self.rank = json['global_rank']
        self.country_code = json['user']['country']['code']
        self.country_name = json['user']['country']['name']

    def to_json(self):
        return json.dumps(self,default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

class CountryPlayer(object):
    def __init__(self,country:Country,best_player:Player,one_above_player:Player):
        self.country = country
        self.best_player = best_player
        self.one_above_player = one_above_player

#endregion

def create_data() -> None:
    print("START")
    token = get_access_token()

    all_players_over_me_list, country_queue = call_osu_api(token)

    close_osu_api(token)

    create_spreadsheet(all_players_over_me_list, country_queue)
    print("END")


def call_osu_api(token:Token):

    all_players_over_me_list = get_all_players_over_me(token)
    country_queue = collect_countries(token)
    #players_queue = collect_players(token,country_queue)

    return all_players_over_me_list, country_queue


def collect_countries(token:Token) -> list[Country]:
    page_num = 1
    country_rank = 1

    country_queue: list[Country] = []
    header = {'Authorization': '{0} {1}'.format(token.token_type, token.token_value)}
    while (True):
        
        response = requests.get(API_COUNTRY_RANKING_URL.format('osu',page_num), headers=header)
        #if cursor = null (meaning that there's no more pages) then break
        country_json = json.loads(response.text)
        if country_json == None or response.status_code != 200 or country_json['cursor'] == None:
            break

        for country in country_json['ranking']:
            country_queue.append(Country(country, country_rank))
            country_rank +=1
            collect_top_player_from_country(token,country_queue[-1])


        page_num += 1
    
    return country_queue


def collect_top_player_from_country(token:Token, country:Country):
    header = {'Authorization': '{0} {1}'.format(token.token_type, token.token_value)}
    response = requests.get(API_COUNTRY_PLAYER_RANKING_URL.format('osu',country.code,'all'), headers=header)
    country_rank_json = json.loads(response.text)

    country.top_country_player = country_rank_json['ranking'][0]['user']['username']
    country.top_country_pp = country_rank_json['ranking'][0]['pp']
    country.top_country_rank = country_rank_json['ranking'][0]['global_rank']

                
'''
Get all people above me in rank
'''
def get_all_players_over_me(token:Token) -> list[Player]:
    api_overall_rankings_url = 'https://osu.ppy.sh/api/v2/rankings/{0}/performance?page={1}'
    player_list: list[Player] = []
    page = 1
    all_players_collected = False
    while not all_players_collected:
        header = {'Authorization': '{0} {1}'.format(token.token_type, token.token_value)}
        response = requests.get(api_overall_rankings_url.format('osu',page), headers=header)
        if response != None and response.status_code == 200:
            for player in json.loads(response.text)['ranking']:
                if player['user']['id'] != USER_ID:
                    player_list.append(Player(player))
                else:
                    all_players_collected = True
                    break
            page += 1
    return player_list



def get_access_token():
    
    token = requests.post('https://osu.ppy.sh/oauth/token',
                          data={'client_id':USER,
                                'client_secret':PASSWORD,
                                'grant_type':'client_credentials',
                                'scope':'public'})

    token_json = json.loads(token.text)
    token = Token(token_json)

    return token
    

def close_osu_api(token:Token): #revoke token
    header = {'Authorization': '{0} {1}'.format(token.token_type, token.token_value)}
    requests.delete('https://osu.ppy.sh/api/v2/oauth/tokens/current',headers=header)
    

def create_spreadsheet(all_players_over_me, country_queue):
    #spreadsheet = open('osuranking' + datetime.today().strftime('%m-%d-%Y') + '.xlsx','a') #if I run it multiple times on the same day, it will overwrite
    #spreadsheet.close()
    '''
    text_dump = json.dumps(all_players_over_me)
    with open('osurankingjson' + datetime.today().strftime('%m-%d-%Y') + '.txt','a') as new_text_doc:
        new_text_doc.write(text_dump)
    new_text_doc.close()
    '''
    df = pandas.DataFrame([o.__dict__ for o in all_players_over_me])
    df.to_csv('osuallrankingjson' + datetime.today().strftime('%m-%d-%Y') + '.csv',index=False)

    df2 = pandas.DataFrame([o.__dict__ for o in country_queue])
    df2.to_csv('osucountryrankingjson' + datetime.today().strftime('%m-%d-%Y') + '.csv',index=False)
if __name__ == '__main__':
    create_data()
