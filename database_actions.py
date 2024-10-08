import random
import sqlite3

url_s_morning_wishes_pics = ['https://i.pinimg.com/564x/3a/ed/03/3aed0339f30db6403112b77f6158cbd4.jpg', 'https://i.pinimg.com/736x/22/d6/e7/22d6e761e3c0d3ead8d6ef0470818c9c.jpg',
     'https://i.pinimg.com/564x/6f/af/9d/6faf9de6f4f1e605ddc7517679d7c40b.jpg', 'https://i.pinimg.com/736x/d4/9a/67/d49a67883c5a956a283bac3d7450b310.jpg',
     'https://i.pinimg.com/736x/d4/56/65/d456654aa7f0358b428552105d5ee58a.jpg', 'https://i.pinimg.com/736x/ed/fc/ed/edfcedec6cde03cda16bd35a6f8e5f34.jpg',
     'https://i.pinimg.com/564x/bd/bc/f7/bdbcf79bfa760c8bfc940f0eecaa2ec2.jpg', 'https://i.pinimg.com/enabled/564x/e5/3f/d3/e53fd34246d2bac5cde3ae09b9976337.jpg',
     'https://i.pinimg.com/564x/25/72/49/2572499ace87bcdae9bca1bdf4d0b305.jpg', 'https://i.pinimg.com/564x/43/28/81/43288164123442464d2440f61acf3a02.jpg', 'https://i.pinimg.com/564x/e9/10/1b/e9101bb2041c933982c730a98feaef62.jpg',
     'https://i.pinimg.com/564x/48/a0/df/48a0df9b7f3f9e9f086e9204eb23e12e.jpg', 'https://i.pinimg.com/564x/df/91/11/df9111005b93b882114971d9a18d5aa9.jpg', 'https://i.pinimg.com/736x/67/d9/8e/67d98e6343893070eb18055b6229d49c.jpg',
     'https://i.pinimg.com/564x/b7/f4/8e/b7f48eb6151572be8bfa35688d122d4d.jpg', 'https://i.pinimg.com/564x/1e/f6/3a/1ef63a35e293f51b8e10fcba33dc46f0.jpg', 'https://i.pinimg.com/564x/f9/04/96/f904960d466c921ec005302bd1d9f667.jpg',
     'https://i.pinimg.com/564x/59/45/f9/5945f96178b6fe94f6cb678e1d6c2273.jpg', 'https://i.pinimg.com/564x/ca/2d/97/ca2d97eaa268ab40e318329f7a97dd02.jpg',
     'https://i.pinimg.com/564x/13/46/ea/1346ea539f546c011b1470965ab41d2e.jpg', 'https://i.pinimg.com/564x/c6/cc/a5/c6cca58401e5a70eda1d4843d657a866.jpg', 'https://i.pinimg.com/enabled/564x/31/18/08/31180828b89f2aaf0596f2316d9ab169.jpg']

audio_paths = ['media/nature_audio/birds_and_rain.mp3', 'media/nature_audio/birds_singing.mp3', 'media/nature_audio/cat_purr.mp3', 'media/nature_audio/gentle_ocean_waves_birdsong_and_gull.mp3',
               'media/nature_audio/happy_birds_singing.mp3', 'media/nature_audio/mocking_birds_singing_by_the_nest.mp3', 'media/nature_audio/nightingale_song.mp3']


def create_db_morning_output():
    conn = sqlite3.connect('morning_output.db')
    c = conn.cursor()
    c.execute(
        "create table if not exists morning_pic_for_overlay (id INTEGER PRIMARY KEY, image TEXT)")

    c.execute(
        "create table if not exists morning_wishes_pic (id INTEGER PRIMARY KEY, image TEXT)")

    c.execute(
        "create table if not exists nature_sounds (id INTEGER PRIMARY KEY, audio TEXT)")

    conn.commit()
    conn.close()


def insert_media_objects(table_name, column_name, media_obj_paths):
    # table_name = 'morning_pic_for_overlay' or 'morning_wishes_pic'
    conn = sqlite3.connect('morning_output.db')
    cursor = conn.cursor()
    for media_obj_path in media_obj_paths:
        cursor.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (media_obj_path,))
    conn.commit()
    conn.close()

def fill_morning_pic_for_overlay_table():
    conn = sqlite3.connect('morning_output.db')
    c = conn.cursor()
    for index in range(1, 11):
        path_to_image =  f'media/morning_pictures_for_overlay/morning_pic_{index}.jpg'
        c.execute("INSERT INTO morning_pic_for_overlay (image) VALUES (?)",
        (path_to_image,))
    conn.commit()
    c.execute("SELECT image FROM morning_pic_for_overlay")
    res = c.fetchall()
    c.close()

def fill_morning_wishes_pic_table():
    insert_media_objects('morning_wishes_pic', 'image', url_s_morning_wishes_pics)

def fill_nature_sounds_table():
    insert_media_objects('nature_sounds', 'audio', audio_paths)

def get_path_morning_wishes_pic():
    conn = sqlite3.connect('morning_output.db')
    c = conn.cursor()
    c.execute("SELECT id FROM morning_wishes_pic")
    all_ids = c.fetchall()
    if not all_ids:
        logging.info(
            'fetching all ids from the table "morning_wishes_pic" resulted in []: No IDs available in the table.')
        return
    all_ids = [container[0] for container in all_ids]
    random_pic_index = random.choice(all_ids)

    c.execute("SELECT image FROM morning_wishes_pic WHERE id = ?",
              (random_pic_index,))
    img = c.fetchone()
    if img is None:
        logging.info('fetching an image with random id from the table "morning_wishes_pic" resulted in (,)')
        return

    img_path_fetched = img[0]
    conn.commit()
    conn.close()
    return img_path_fetched

def select_random_pic_for_overlay__copy__one_modify_by_overlaying_text__and_delete():
    conn = sqlite3.connect('morning_output.db')
    c = conn.cursor()
    c.execute("SELECT id FROM morning_pic_for_overlay")
    all_ids = c.fetchall()
    if not all_ids:
        print("No IDs available in the table.")
        logging.info('fetching all ids from the table "morning_pic_for_overlay" resulted in []: No IDs available in the table.')
        return
    all_ids = [container[0] for container in all_ids]
    random_pic_index = random.choice(all_ids)

    c.execute("SELECT image FROM morning_pic_for_overlay WHERE id = ?",
               (random_pic_index,))
    img = c.fetchone()
    if img is None:
        print("No image found for the selected ID.")
        logging.info('fetching an image with random id from the table "morning_pic_for_overlay" resulted in (,)')
        return
    img_path_fetched = img[0]
    c.execute(
        "INSERT INTO morning_pic_for_overlay (image) VALUES (?)",
        (img_path_fetched,))
    c.execute("DELETE FROM morning_pic_for_overlay WHERE id = ?", (random_pic_index,))
    conn.commit()
    conn.close()
    return  img_path_fetched



if __name__ == "__main__":
    #create_db_morning_output()
    #fill_morning_pic_for_overlay_table()
    #fill_morning_wishes_pic_table()
    #fill_nature_sounds_table()
    pass

