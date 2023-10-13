import random
from app.util.database_utils import artgen_sql, artgenstyle_sql
import openai


def generate_dalle_prompt():
    all_genres = [record.genre_name for record in artgen_sql.query.all()]

    # If there are no genres, raise an error
    if not all_genres:
        raise ValueError("No genres available in the database.")

    # Randomly select a genre
    genre_name = random.choice(all_genres)
    record = artgen_sql.query.filter_by(genre_name=genre_name).first()

    all_styles = [style.art_style for style in artgenstyle_sql.query.all()]

    columns = [
        record.place_1, record.place_2, record.place_3, record.place_4, record.place_5,
        record.role_1, record.role_2, record.role_3, record.role_4, record.role_5,
        record.item_1, record.item_2, record.item_3, record.item_4, record.item_5,
        record.symbol_1, record.symbol_2, record.symbol_3, record.symbol_4, record.symbol_5,
        record.concept_1, record.concept_2, record.concept_3, record.concept_4, record.concept_5,
        record.event_1, record.event_2, record.event_3, record.event_4, record.event_5
    ]
    random_value = random.choice([col for col in columns if col])  # Selecting non-null values

    # 3. Randomly select a style from the provided list
    random_style = random.choice(all_styles)
    # 4. Use the selected genre, value, and style to create a prompt
    prompt = f"Genre: {genre_name}, Picture Subject: {random_value}, in the Style of: {random_style}"
    print(f"Style Guidelines: {prompt}")
    # 5. Send the prompt to the GPT-4 model to craft a DALL-E prompt
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful creative assistant."},
            {"role": "user",
             "content": f"Craft this into a concise and creatively interesting DALL-E prompt: {prompt} Stay as true to these style guidelines as possible. Thanks!"}
        ],
        temperature=0.6,
    )

    return response["choices"][0]["message"]["content"]


def generate_images_dalle(prompt):
    print("Generating images...")
    print(f"Prompt: {prompt}")
    image_urls = []

    for i in range(5):
        # Call the OpenAI API
        generation_response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512",
            response_format="url",
        )

        # Extract the generated image URL
        generated_image_url = generation_response["data"][0]["url"]

        # Add the URL to the list of image URLs
        image_urls.append(generated_image_url)

    return image_urls
