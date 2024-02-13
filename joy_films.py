""" parsing m1.joyfilms.xyz """
import sys
from datetime import datetime
import requests, fake_useragent
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query

def p(text, *args):
    print(text, *args, sep=' / ', end='\n')

def get_html(url_page):
    header = { 'User-Agent':str(fake_useragent.UserAgent().google), }

    try:
        page = requests.get(url=url_page, headers = header, timeout = 10)
        return page.text
    
    except Exception as e:
        print(sys.exc_info()[1])
        return False

def get_all_links(html):
    """ links is url film """
    if html is False:
        False

    soup = BeautifulSoup(html, 'lxml')
    selection_list = soup.find('div', {'id':'pdopage'})

    links = []
    if selection_list is not None:
        for r in selection_list.find_all('div', {'class':'catalog-main-item'}):
            # add item for links
            try:
                i_href = r.find('a', {'class':'film-item'}).get("href").strip()
                i_name = r.find('h2', {'class':'film-item-title'}).text.strip()
                i_genre = r.find('div', {'class':'film-item-genres'}).text.strip()
                i_type = r.find('div', {'class':'film-item-type'}).text.strip()
                i_episode = r.find('div', {'class':'film-item-episode'})
                i_image = r.find('div', {'class':'film-item-image'})
                i_rating = i_image.find('div', {'class':'film-item-rating'})
                i_img = i_image.find('img')

                row = {}
                row["fid"] = str(i_href).replace('/','')
                row["name"] = i_name
                row["genre"] = i_genre
                row["type"] = i_type

                if i_episode is not None:
                    row["episode"] = i_episode.text.strip()
    
                if i_img is not None:
                    row["img"] = i_img.get('data-src')
                    row["img_title"] = i_img.get('title')

                if i_rating is not None:
                    rating_oll = []
                    for rating in i_rating.find_all('div', {'class':'film-item-rating-kp'}):
                        rt = rating.text.strip()
                        rating_oll.append(rt)
  
                    row["rating"] = rating_oll

                links.append(row)

            except Exception as e:
                    print(sys.exc_info()[1])
                    continue

    return links

def get_page(html):
    """ page in json """
    pg = {}
    soup = BeautifulSoup(html, 'lxml')
    try:
        p_url = soup.find('meta', {'property':'og:url'}).get("content")
        p_img = soup.find('meta', {'property':'og:image'}).get("content")
        p_title = soup.find('title').text.strip()
        p_table = soup.find('table', {'class':'film-info-table'})
        p_content = soup.find('div', {'class':'film-content'})

        pg['url'] = p_url
        pg['title'] = p_title
        pg['img_meta'] = p_img

        if p_content is not None:
            p_text = p_content.find('p').text.strip()
            if p_text is not None:
                pg['description'] = p_text

        if p_table is not None:
            tbl = []
            for tr in p_table.find_all('tr'):
                td = []
                for tt in tr.find_all('td'):
                    td.append(tt.text.strip())
                
                tbl.append(td)

            if len(tbl) > 0:
                pg['table'] = tbl

    except Exception as e:
        print(sys.exc_info()[1])        

    return pg

def set_link():
    """ set and parsing links for films """
    db = TinyDB('./json/links.json')

    for num, i in enumerate(range(851), 1):

        if num > 10:
            break

        if i == 0:
            url = "https://m1.joyfilms.xyz/"
        else:
            url = f"https://m1.joyfilms.xyz/?page={num}&pageId=&hash=10f1f1ca23d82390c0605447a241f1d58b0230d4"
        
        link_film = get_all_links(get_html(url))
        link_list = db.insert_multiple(link_film)
        p(link_list)

def set_films():  
    """ set table films """
    db_f = TinyDB('./json/films.json')
    for f in TinyDB('./json/links.json').all():
        """ """
        url_film = f"https://m1.joyfilms.xyz/{f['fid']}"
        pg = get_page(get_html(url_film))
        pj = {**f, **pg}

        db_fid = db_f.insert(pj)
        p(db_fid, url_film, f['name'])

if __name__ == "__main__":
    
    # 1.
    # set_link()
    
    # 2.
    # for f in TinyDB('./json/links.json').all():
    #     p(f['fid'], f['name'], f['type'])
    
    # 3.
    # set_films()

    # 4.
    for f in TinyDB('./json/films.json').all():
        p(f['fid'], f['name'], f['type'])
        p(' / '.join([' → '.join(x) for x in f['table']]))