import requests
import re
import os
import csv


## Korak 1: Definicija funkcij za zajem podatkov


jobs_frontpage_url = 'https://www.studentski-servis.com/studenti/prosta-dela'
jobs_directory = 'jobs'
frontpage_filename = 'index_jobs.html'
csv_filename = 'jobs.csv'


def download_url_to_string(url):
    """Funkcija kot argument sprejme niz in poskusi vrniti vsebino te spletne
    strani kot niz. V primeru, da med izvajanje pride do napake vrne None.
    """
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print("Napaka pri povezovanju do:", url)
        return None
    if r.status_code == requests.codes.ok:
        return r.text
    else:
        print("Napaka pri prenosu strani:", url)
        return None


def save_string_to_file(text, directory, filename):
    """Funkcija zapiše vrednost parametra "text" v novo ustvarjeno datoteko
    locirano v "directory"/"filename", ali povozi obstoječo. V primeru, da je
    niz "directory" prazen datoteko ustvari v trenutni mapi.
    """
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None


def save_frontpage(directory, filename):
    """Funkcija vrne celotno vsebino datoteke "directory"/"filename" kot niz"""
    text = download_url_to_string(jobs_frontpage_url)
    save_string_to_file(text, directory, filename)
    return None


## Korak 2: Obdelava podatkov


def read_file_to_string(directory, filename):
    """Funkcija vrne celotno vsebino datoteke "directory"/"filename" kot niz"""
    path = os.path.join(directory, filename)
    with open(path, 'r', encoding='utf-8') as file_in:
        return file_in.read()


def page_to_ads(page_content):
    """Funkcija poišče posamezne oglase, ki se nahajajo v spletni strani in
    vrne njihov seznam"""
    rx = re.compile(r'<div class=\"col-lg-9 col-md-6\">(.*?)</article>',
                    re.DOTALL)
    ads = re.findall(rx, page_content)
    return ads


def get_dict_from_ad_block(block):
    """Funkcija iz niza za posamezen oglasni blok izlušči podatke o imenu,
    lokaciji, neto urni postavki, trajanju in delovniku ter vrne slovar, 
    ki vsebuje ustrezne podatke"""
    rx = re.compile(r'<h3 .*?>(?P<name>.*?)</h3>'
                    r'.*?<li>\s*<svg.*?</svg>\s*(?P<location>.*?)\s*?</li>'
                    r'.*?<strong>(?P<payment_neto>\d+?\D\d+?.*?)</strong>'
                    r'.*?<li>Trajanje: <strong>(?P<duration>.*?)</strong></li>',
                    re.DOTALL)
    data = re.search(rx, block)
    ad_dict = data.groupdict()

    # Ker nimajo vsi oglasi podatka o številu prostih mest, dodamo vzorec:
    rloc = re.compile(r'.*?<li>Št\. prostih mest: <strong>(?P<vacancies>\d+?)</strong></li>')
    locdata = re.search(rloc, block)
    if locdata is not None:
        ad_dict['vacancies'] = locdata.group('vacancies')
    else:
        ad_dict['vacancies'] = 'Unknown'

    return ad_dict


def ads_from_file(filename, directory):
    """Funkcija prebere podatke v datoteki "directory"/"filename" in jih
   pretvori (razčleni) v pripadajoč seznam slovarjev za vsak oglas posebej."""
    page = read_file_to_string(filename, directory)
    blocks = page_to_ads(page)
    ads = [get_dict_from_ad_block(block) for block in blocks]
    return ads


def ads_frontpage():
    return ads_from_file(jobs_directory, frontpage_filename)


## Korak 3: Shranjevanje podatkov


def write_csv(fieldnames, rows, directory, filename):
    """
    Funkcija v csv datoteko podano s parametroma "directory"/"filename" zapiše
    vrednosti v parametru "rows" pripadajoče ključem podanim v "fieldnames"
    """
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return None


def write_job_ads_to_csv(ads, directory, filename):
    """Funkcija vse podatke iz parametra "ads" zapiše v csv datoteko podano s
    parametroma "directory"/"filename". Funkcija predpostavi, da so ključi vseh
    slovarjev parametra ads enaki in je seznam ads neprazen."""
    assert ads and (all(j.keys() == ads[0].keys() for j in ads))
    write_csv(ads[0].keys(), ads, directory, filename)


def main(redownload=True, reparse=True):
    #save_frontpage(jobs_directory, frontpage_filename)
    ads = page_to_ads(read_file_to_string(jobs_directory, frontpage_filename))
    ads_nice = [get_dict_from_ad_block(ad) for ad in ads]
    write_job_ads_to_csv(ads_nice, jobs_directory, csv_filename)


if __name__ == '__main__':
    main()