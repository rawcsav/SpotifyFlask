import random
from datetime import datetime

import openai

from app.database import artgenstyle_sql, artgenurl_sql, db, artgen_sql


def select_random_elements(genres_list=None):
    if genres_list:
        all_genres = [record.genre_name for record in
                      artgen_sql.query.filter(artgen_sql.genre_name.in_(genres_list)).all()]
    else:
        all_genres = [record.genre_name for record in artgen_sql.query.all()]

    if not all_genres:
        raise ValueError("No genres available in the database.")

    genre_name = random.choice(all_genres)
    record = artgen_sql.query.filter_by(genre_name=genre_name).first()

    # Fetch all art styles along with their corresponding gen_style values
    all_styles = [(style.art_style, style.gen_style) for style in artgenstyle_sql.query.all()]
    if not all_styles:
        raise ValueError("No styles available in the database.")

    art_style, gen_style = random.choice(all_styles)

    columns = [
        record.place_1, record.place_2, record.place_3, record.place_4, record.place_5,
        record.role_1, record.role_2, record.role_3, record.role_4, record.role_5,
        record.item_1, record.item_2, record.item_3, record.item_4, record.item_5,
        record.symbol_1, record.symbol_2, record.symbol_3, record.symbol_4, record.symbol_5,
        record.event_1, record.event_2, record.event_3, record.event_4, record.event_5
    ]

    random_attribute = random.choice([col for col in columns if col])

    return genre_name, art_style, random_attribute, gen_style


def generate_dalle_prompt(genre_name, art_style, random_attribute):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": "You are a helpful creative assistant. You will be provided with randomized attributes relating to music genres and artistic styles. Help the user craft the most optimal and most detailed possible DALL-E prompt. Fill in any [SUBJECT] appropriately. Under no circumstances will you return anything besides the prompt."},
            {"role": "user",
             "content": f"Craft this into a vivid and detailed DALL-E prompt that accurately captures the essence of {art_style} while highlighting the {genre_name} music genre. Ensure {random_attribute} is the focal point. Fill in any [SUBJECT] appropriately. Do nothing but send back the prompt."}
        ],
        temperature=0.7,
        max_tokens=300,
    )

    return response.choices[0].message.content


def generate_images_dalle(prompt, style, quality='standard'):
    image_urls = []

    for i in range(3):
        generation_response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality=quality,
            style=style,
            n=1,
        )

        generated_image_url = generation_response.data[0].url

        image_urls.append(generated_image_url)

    return image_urls


def generate_and_save_images(playlist_id, genre_name=None, prompt_text=None):
    if prompt_text is None:
        genre_name, art_style, random_attribute, gen_style = select_random_elements(genre_name)
        prompt = generate_dalle_prompt(genre_name, art_style, random_attribute)
    else:
        prompt = prompt_text
        genre_name = "Refresh"
        art_style = "Refresh"
        random_attribute = "Refresh"
        gen_style = "vivid"
    print(genre_name, art_style, random_attribute, prompt, gen_style)
    image_urls = generate_images_dalle(prompt, gen_style)
    current_time = datetime.utcnow()

    for url in image_urls:
        new_artgenurl_record = artgenurl_sql(
            url=url,
            genre_name=genre_name,
            art_style=art_style,
            random_attribute=random_attribute,
            prompt=prompt,
            playlist_id=playlist_id,
            timestamp=current_time
        )

        db.session.merge(new_artgenurl_record)

    db.session.commit()

    return image_urls, prompt
