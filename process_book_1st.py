import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configure the OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")
client = OpenAI(api_key=api_key)


# Remove #### from the prompt
def remove_delimiters(prompt):
    return prompt.replace("####", "").strip()


def get_completion(prompt, model="gpt-4o"):
    messages = [
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
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(data)
    except Exception as e:
        print(f"Error writing to file: {e}")


# Example usage
file_path = "books/mem_post_bras_cubas.txt"  # Replace with your actual file path
paragraphs_list = extract_paragraphs(file_path)
output_file = "books/mem_post_bas_cubas_atualizado.txt"  # Replace with your desired output file path

paragrafo_inicial = 0
paragrafo_final = 10000

if not paragraphs_list:
    print("No paragraphs extracted. Exiting program.")
else:
    output_data = ""
    for idx, paragraph in enumerate(paragraphs_list, start=1):

        print(f"Processing paragraph {idx}...")

        prompt_adjust = f"""
        Para o texto a seguir, delimitado por ####, converta a grafia das palavras
        para o português corrente do Brasil. Não faça nenhum comentário adicional.

        #### {paragraph} ####
        """

        if paragrafo_inicial <= idx <= paragrafo_final:
            adjusted_text = get_completion(prompt=prompt_adjust)
            if not adjusted_text:
                continue
            else:
                adjusted_text = remove_delimiters(adjusted_text)
                print(f"{adjusted_text}")
                output_data += f"{adjusted_text}\n\n"
        elif idx > paragrafo_final:
            break
        else:
            output_data += f"{paragraph}\n\n"

    # Save the processed data to a file
    save_to_file(output_data, output_file)
    print(f"Processed data saved to {output_file}")
