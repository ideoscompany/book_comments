import os
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables from the .env file
load_dotenv()

# Configure the OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")
client = OpenAI(api_key=api_key)


def get_completion(prompt, model="gpt-4o"):
    messages = [
        {
            "role": "system",
            "content": "Você é um especialista na lingua portuguesa e em Machado de Assis",
        },
        {"role": "user", "content": prompt},
    ]
    try:
        response = client.chat.completions.create(
            model=model, messages=messages, temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in getting completion: {e}")
        return None


def extract_paragraphs(file_path):
    """Extract paragraphs from a text file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

    paragraphs = content.split("\n\n")

    # Remove any leading/trailing whitespace from each paragraph and any empty paragraphs
    paragraphs = [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]

    return paragraphs


def save_to_file(data, file_path):
    """Save processed data to a text file."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(data)
    except Exception as e:
        print(f"Error writing to file: {e}")


# Example usage
file_path = (
    "books/mem_post_bras_cubas_atualizado.txt"  # Replace with your actual file path
)
paragraphs_list = extract_paragraphs(file_path)
output_file = "books/mem_post_bras_cubas_comentado.txt"  # Replace with your desired output file path

inicio = 20
fim = 10000

if not paragraphs_list:
    print("No paragraphs extracted. Exiting program.")
else:
    output_data = ""
    for idx, paragraph in tqdm(
        enumerate(paragraphs_list, start=1),
        total=len(paragraphs_list),
        desc="Processing paragraphs",
    ):
        if (
            paragraph
            == "*** END OF THE PROJECT GUTENBERG EBOOK MEMÓRIAS PÓSTUMAS DE BRÁS CUBAS ***"
        ):
            break

        print(f"Processing paragraph {idx}...")

        # Count the number of words in the paragraph
        words = paragraph.split()
        output_data += f"{paragraph}\n\n"

        if len(words) > 5 and inicio <= idx <= fim:
            prompt_comments = f"""
            Para o texto a seguir, delimitado por ####

            1. Extraia as palavras raramente usadas hoje em dia e explique-as de forma concisa.
               O resultado deve ser um json com chaves aninhadas Palavras e palavra.
            2. Comente suscintamente o parágrafo. O resultado deve ser um json com a chave Comentario.

            #### {paragraph} ####
            """

            completion = get_completion(prompt=prompt_comments, model="gpt-4o")
            if completion:
                output_data += f"{completion}\n\n"
        elif idx > fim:
            break

    # Save the processed data to a file
    save_to_file(output_data, output_file)
    print(f"Processed data saved to {output_file}")
