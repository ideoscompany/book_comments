import os
import re
import json
from ebooklib import epub
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

import json


def extract_json_from_list(input_list):
    """
    Extracts and parses the JSON object from a given list containing a string with JSON data.

    Args:
        input_list (list): The input list containing a string with JSON data.

    Returns:
        dict: The parsed JSON object.
    """
    # Check if the input is a list and has at least one element
    if isinstance(input_list, list) and input_list:
        # Get the first element from the list
        json_string = input_list[0]

        # Step 1: Remove unnecessary parts of the string
        cleaned_string = json_string.strip("['json").strip("']")

        # Step 2: Load the JSON string
        cleaned_string = (
            cleaned_string.strip()
        )  # Remove any leading/trailing whitespace
        json_data = json.loads(cleaned_string)

        return json_data
    else:
        raise ValueError(
            "Input must be a non-empty list containing a string with JSON data"
        )


def remove_delimited_parts(content):
    # Extract and remove parts of the content delimited by triple backticks
    json_matches = re.findall(r"```(.*?)```", content, flags=re.DOTALL)
    content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    # json_objects = [json.loads(match.strip()) for match in json_matches]
    # print(1, json_matches)
    if json_matches != []:
        json_objects = extract_json_from_list(json_matches)
    else:
        json_objects = None
    # print(2, json_objects)
    return content, json_objects


def remove_specific_text(content):
    content = re.sub(
        r"1\. Extração.*?(?=\n\n|\Z)", "", content, flags=re.MULTILINE | re.DOTALL
    )
    content = re.sub(
        r"^2\. Comentário.*?(?=\n\n|\Z)", "", content, flags=re.MULTILINE | re.DOTALL
    )
    return content


def read_and_split_book(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Remove delimited parts and collect JSON objects
    # content, json_objects = remove_delimited_parts(content)

    # Remove the specific texts from all chapters
    content = remove_specific_text(content)

    # Split content by the "CAPÍTULO" keyword, keeping the keyword in the split parts
    parts = re.split(r"(CAPÍTULO\s+\S+)", content)

    # Merge chapter titles back with their content
    separated_parts = [parts[0].strip()]  # The text before the first chapter
    for i in range(1, len(parts) - 1, 2):
        chapter_title = parts[i].strip()
        chapter_content = parts[i + 1].strip()
        separated_parts.append(f"{chapter_title} \n\n {chapter_content}")

    return separated_parts


def create_paragraph_from_json(json_obj):
    palavras = json_obj.get("Palavras", {})
    # print(3, palavras)
    comentario = json_obj.get("Comentario", "")

    if (
        palavras != []
        and palavras != {}
        and palavras != {"palavra": []}
        and palavras != {"raramente_usadas": []}
    ):
        palavras_text = "<ul>"
        # print(4, palavras)
        for palavra, explicacao in palavras.items():
            palavras_text += f"<li><strong>{palavra}:</strong> {explicacao}</li>"
        palavras_text += "</ul>"
    else:
        palavras_text = ""

    if comentario != "":
        comentario_text = (
            f"<p><strong>Comentário sobre o parágrafo:</strong> {comentario}</p>"
        )
    else:
        comentario_text = ""

    return f"{palavras_text}{comentario_text}"


def create_epub(book_parts, output_file):

    book = epub.EpubBook()
    book.set_identifier("id123456")
    book.set_title("Memórias Póstumas de Brás Cubas")
    book.set_language("pt")

    book.add_author("Machado de Assis")

    # Create the first part (text before the first chapter)
    first_part = epub.EpubHtml(title="Introdução", file_name="intro.xhtml", lang="pt")
    first_part.content = (
        f'<h1>Introdução</h1><p>{book_parts[0].replace("\n", "<br/>")}</p>'
    )
    book.add_item(first_part)

    # Create chapters
    chapters = []

    for idx, chapter in enumerate(book_parts[1:], start=1):

        # Convert newlines to paragraph breaks
        paragraphs = chapter.split("\n\n")

        chapter_title = paragraphs[0] + " - " + paragraphs[1]
        paragraphs = paragraphs[2:]

        enriched_paragraphs = []
        for paragraph in paragraphs:

            paragraph, json_objects = remove_delimited_parts(paragraph)

            if paragraph != "":
                paragraph = "<strong>Parágrafo:</strong> " + paragraph

            # if paragrph includes the word Damiao
            # if "Damião" in paragraph:
            #     os._exit(0)

            enriched_paragraphs.append(paragraph.replace("\n", "<br/>"))
            if json_objects:
                enriched_paragraphs.append(create_paragraph_from_json(json_objects))

        enriched_content = "</p><p>".join(enriched_paragraphs)

        chap = epub.EpubHtml(
            title=chapter_title, file_name=f"chap_{idx}.xhtml", lang="pt"
        )
        chap.content = f"<h1>{chapter_title}</h1><p>{enriched_content}</p>"
        book.add_item(chap)
        chapters.append(chap)

    # Define Table of Contents
    book.toc = (
        epub.Link("intro.xhtml", "Introdução", "intro"),
        (epub.Section("Capítulos"), tuple(chapters)),
    )

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS style
    style = "body { font-family: Arial, sans-serif; }"
    nav_css = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style
    )
    book.add_item(nav_css)

    # Create spine
    book.spine = ["nav", first_part] + chapters

    # Write to the file
    epub.write_epub(output_file, book, {})


# Main program
file_path = (
    "books/mem_post_bras_cubas_comentado.txt"  # Replace with your actual file path
)
book_parts = read_and_split_book(file_path)
output_file = (
    "Memorias_Postumas_de_Bras_Cubas.epub"  # Replace with your desired output file path
)

create_epub(book_parts, output_file)

print(f"Ebook saved to {output_file}")

# Finish application
os._exit(0)
