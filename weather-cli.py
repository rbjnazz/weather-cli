#!/usr/bin/env python3
import json
import yaml
import requests
from rich.console import Console
from pathlib import Path


DIR = Path(__file__)
CONSOLE = Console()
BV = u'\u2502'
BH = u'\u2500'
BTL = u'\u250C'
BTR = u'\u2510'
BBL = u'\u2514'
BBR = u'\u2518'


def borderize(string_info):
    target_len = 50
    string_len = len(string_info)
    if string_len == 1:
        return f'{string_info}\n'
    elif string_len == target_len:
        return f' {string_info}\n'
    else:
        whitespace_len = target_len - string_len - 3
        whitespace = ' ' * whitespace_len
        new_string = f' {BV} {string_info}{whitespace}{BV}\n'
        return new_string


def join_strings(ascii_dir, status_code, info):
    json_file = DIR.parent / 'weather-conditions.json'
    with open(json_file, encoding='utf-8') as jsonf:
        weather_conditions = json.load(jsonf)
        for key in weather_conditions:
            if key['code'] == status_code:
                folder_dir = DIR.parent / 'ascii-art' / ascii_dir
                txt_file = folder_dir / f'{key["icon"]}.txt'
                with open(txt_file, encoding='utf-8') as txtf:
                    ascii_art = txtf.readlines()
                    result = ''
                    for line, k in zip(ascii_art, info.keys()):
                        result += line.rstrip() + borderize(info[k])
                    return result
            else:
                continue


def user_input():
    user_query = input('Search [City/Location] [Country]: ')
    if user_query == '':
        auto_ip = requests.get(
                'https://api.ipify.org'
                ).content.decode('utf-8')
        return auto_ip
    else:
        return user_query


def get_api_key():
    try:
        yaml_file = DIR.parent / 'api-key.yaml'
        with open(yaml_file) as yamlf:
            api_key = yaml.safe_load(yamlf)
            return api_key['key']
    except (FileNotFoundError, KeyError):
        with open(yaml_file, 'w') as yamlf:
            user_api_key = input('Enter your API KEY: ')
            if len(user_api_key) == 50:
                yaml.dump({'key': user_api_key}, yamlf)
                CONSOLE.print(
                        ':white_check_mark:[bold green] API KEY saved')
                return user_api_key
            else:
                CONSOLE.print(
                        ':x:[bold red] API KEY must be 50 characters long!')
                exit()


def info_dict(curr, loc):
    degree = u'\u00b0'
    data = {
        1: f'{BTL}{BH * 48}{BTR}',
        2: 'Now:',
        3: f'{curr["temp_c"]}{degree}C | {curr["temp_f"]}{degree}F',
        4: f'{curr["condition"]["text"]}',
        5: f'{loc["name"]}{", " + loc["region"]}',
        6: f'{loc["country"]}',
        7: f'{loc["localtime"]}',
        8: f'{BV}{BH * 48}{BV}',
        9: 'Forecast:',
        10: (f'Feels like: {curr["feelslike_c"]}{degree}C '
             f'| {curr["feelslike_f"]}{degree}F'),
        11: f'Humidity: {curr["humidity"]}%',
        12: f'Cloud cover: {curr["cloud"]}%',
        13: f'UV index: {curr["uv"]}',
        14: (f'Precipitation: {curr["precip_mm"]} mm '
             f'| {curr["precip_in"]} in'),
        15: (f'Pressure: {curr["pressure_mb"]} millibar '
             f'| {curr["pressure_in"]} in'),
        16: f'Visibility: {curr["vis_km"]} km | {curr["vis_miles"]} mi',
        17: (f'Wind direction: {curr["wind_degree"]}'
             f'{degree} | {curr["wind_dir"]}'),
        18: (f'Wind gust: {curr["gust_kph"]} kph '
             f'| {curr["gust_mph"]} mph'),
        19: (f'Wind speed max: {curr["wind_kph"]} kph '
             f'| {curr["wind_mph"]} mph'),
        20: f'Last update: {curr["last_updated"]}',
        21: f'{BBL}{BH * 48}{BBR}'
        }
    return data


def main():
    try:
        api_key = get_api_key()
        query = {'q': user_input()}
        stat = 'Collecting data from weatherapi-com.p.rapidapi.com'
        with CONSOLE.status(f'[bold green]{stat}\n', spinner='weather'):
            url = 'https://weatherapi-com.p.rapidapi.com/current.json'
            headers = {
                'X-RapidAPI-Key': api_key,
                'X-RapidAPI-Host': 'weatherapi-com.p.rapidapi.com'
            }
            response = requests.request(
                    'GET', url, headers=headers, params=query)
            result_json = response.json()
            location = result_json['location']
            current = result_json['current']
            if response.status_code == 400:
                error = result_json['error']
                CONSOLE.print(f':x:[bold red] {error["message"]}')
            else:
                info = info_dict(current, location)
                ascii_banner = DIR.parent / 'ascii-art/banner.txt'
                with open(ascii_banner, encoding='utf-8') as txtf:
                    banner = txtf.readlines()
                    banner_line = []
                    for line in banner:
                        banner_line.append(line.rstrip())
                    for k, v in zip(range(len(info) + 1, 31), range(0, 10)):
                        info[k] = banner_line[v]
                if current['is_day']:
                    day_report = join_strings(
                            'day',
                            current['condition']['code'],
                            info)
                    print(day_report)
                else:
                    night_report = join_strings(
                            'night',
                            current['condition']['code'],
                            info)
                    print(night_report)
    except KeyError:
        CONSOLE.print(f':x:[bold red] {result_json["error"]["message"]}')
    except requests.ConnectionError as err:
        CONSOLE.print(
                ':question_mark:[bold red] No internet connection.\n',
                err)


if __name__ == '__main__':
    main()
