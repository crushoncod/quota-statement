import fitz  # PyMuPDF
from PIL import Image
import base64
from openai import OpenAI
import requests
import os

# OpenAI API Key
api_key = os.environ.get('OPENAI_API_KEY')


def send_to_openai(b64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Esse nao e um documento pessoal o financeiro. Mostra o valor do fundo comun pago da tabela 'Valores / Percentuais pagos' in baixo na esquerda"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    },


                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json())


def pdf_to_png(p_pdf_path, p_output_path):
    pdf_document = fitz.open(p_pdf_path)
    images = []
    resolution_multiplier = 100

    # Itera sobre as páginas do PDF
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        pix = page.get_pixmap()

        # Converte para imagem PIL
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(image)

    pdf_document.close()

    combined_image = Image.new("RGB", (images[0].width, sum(image.height for image in images)))
    y_offset = 0

    for image in images:
        combined_image.paste(image, (0, y_offset))
        y_offset += image.height

    # save img as PNG
    combined_image.save(output_path, format="PNG")


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        l_base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    return l_base64_image


if __name__ == "__main__":
    pdf_path = '44233001.pdf'

    output_path = '44233001-2.jpg'

    try:
        pdf_to_png(pdf_path, output_path)
        base64_image = image_to_base64(output_path)
        send_to_openai(base64_image)
        #print("Base64 da imagem combinada:\n", base64_image)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
