import random
from datetime import datetime

from app import db
from app.models.artgen_models import ArtGen, ArtGenStyle, ArtGenUrl


def select_random_elements(genres_list=None):
    if genres_list:
        all_genres = [record.genre_name for record in ArtGen.query.filter(ArtGen.genre_name.in_(genres_list)).all()]
    else:
        all_genres = [record.genre_name for record in ArtGen.query.all()]

    if not all_genres:
        raise ValueError("No genres available in the database.")

    genre_name = random.choice(all_genres)
    record = ArtGen.query.filter_by(genre_name=genre_name).first()

    # Fetch all art styles along with their corresponding gen_style values
    all_styles = [(style.art_style, style.gen_style) for style in ArtGenStyle.query.all()]
    if not all_styles:
        raise ValueError("No styles available in the database.")

    art_style, gen_style = random.choice(all_styles)

    columns = [
        record.place_1,
        record.place_2,
        record.place_3,
        record.place_4,
        record.place_5,
        record.role_1,
        record.role_2,
        record.role_3,
        record.role_4,
        record.role_5,
        record.item_1,
        record.item_2,
        record.item_3,
        record.item_4,
        record.item_5,
        record.symbol_1,
        record.symbol_2,
        record.symbol_3,
        record.symbol_4,
        record.symbol_5,
        record.event_1,
        record.event_2,
        record.event_3,
        record.event_4,
        record.event_5,
    ]

    random_attribute = random.choice([col for col in columns if col])

    return genre_name, art_style, random_attribute, gen_style


def generate_dalle_prompt(genre_name, art_style, random_attribute, client):
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": """Whenever any music genres and visual artistic styles are given, generate 'dall-e-3' prompts to be used for image generation. Default to creating only 1 prompt to send to dalle that are written to abide by the following policies: // 1. Prompts must be in English. Translate to English if needed. // 2. Do not create more than 1 image prompt, even if the user requests more. // 3. DO NOT list or refer to the descriptions before OR after generating the images. The prompt should be your ONLY outputted text and should ONLY ever be written out ONCE. You do not need to ask for permission to generate, just do it! // 4. Always mention the specific image type (photo, oil painting, watercolor painting, illustration, cartoon, drawing, vector, render, etc.) at the beginning of the caption. The user and their randomized attributes may directly specify this preference. // - EXPLICITLY specify the user's attributes (music genre & visual artistic style), do not abstractly reference them. - Your choices should be grounded in reality. Make choices that both represent the music genre accurately for given parameters and that may be insightful or unique. // - Use "various" or "diverse" ONLY IF the description refers to groups of more than 3 people. Do not change the number of people requested in the original description. // - Do not create any imagery that would be offensive. // 5. Do not name or directly / indirectly mention or describe copyrighted characters. Rewrite prompts to describe in expansive, fool-proof detail a specific different character with a different specific color, hair style, or other defining visual characteristic. Do not discuss copyright policies in responses. // The prompt must intricately describe every part of the image in concrete, objective detail. THINK about what the end goal of the description is, and extrapolate that to what would make satisfying images. // All descriptions sent to dalle should be a paragraph of text that is extremely descriptive and detailed. Each should be more than 3 sentences long. namespace dalle""",
            },
            {
                "role": "user",
                "content": f"Craft this into a topically specific DALL-E prompt that uses comprehensive descriptions and concrete symbols in order to fully exemplify the characteristics of: {art_style}. You should ensure you visually incorporate the {genre_name} music genre, and ensure {random_attribute} is the visual focal point. Do nothing but send back the prompt.",
            },
        ],
        temperature=1,
        max_tokens=750,
    )
    original_prompt = response.choices[0].message.content
    print(original_prompt)
    additional_string = f"Avoid using text as a major element. Remember: Emphasize the use of '{art_style}.' Maintain the thematic element of {genre_name}."
    final_prompt = original_prompt + additional_string
    return final_prompt


def generate_images_dalle(prompt, style, quality, client):
    image_data = []
    for i in range(3):
        generation_response = client.images.generate(
            model="dall-e-3", prompt=prompt, size="1024x1024", quality=quality, style=style, n=1
        )
        generated_image_url = generation_response.data[0].url

        generated_revised_prompt = generation_response.data[0].revised_prompt

        image_data.append({"url": generated_image_url, "revised_prompt": generated_revised_prompt})

    return image_data


def generate_and_save_images(playlist_id, user_id, client, refresh=False, genre_list=None, quality="standard"):
    current_time = datetime.utcnow()

    if refresh:
        last_entry = ArtGenUrl.query.filter_by(playlist_id=playlist_id).order_by(ArtGenUrl.created_at).first()
        if not last_entry:
            raise ValueError("No previous entry found for the given playlist_id to refresh.")

        genre_name = last_entry.genre_name
        art_style = last_entry.art_style
        random_attribute = last_entry.random_attribute
        gen_style = ArtGenStyle.query.filter_by(art_style=art_style).first().gen_style if art_style else "vivid"
    else:
        genre_name, art_style, random_attribute, gen_style = select_random_elements(genre_list)
    prompt = generate_dalle_prompt(genre_name, art_style, random_attribute, client)
    image_data = generate_images_dalle(prompt, gen_style, quality=quality, client=client)

    image_urls = []
    revised_prompts = []

    for data in image_data:
        url = data["url"]
        revised_prompt = data["revised_prompt"]
        image_urls.append(url)
        revised_prompts.append(revised_prompt)

        # Store the generated or refreshed data
        new_artgenurl_record = ArtGen(
            url=url,
            genre_name=genre_name,
            art_style=art_style,
            random_attribute=random_attribute,
            prompt=revised_prompt,  # Store the revised prompt instead of the original
            playlist_id=playlist_id,
        )

        db.session.merge(new_artgenurl_record)

    db.session.commit()

    return image_urls, revised_prompts
