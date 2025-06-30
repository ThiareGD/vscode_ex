#!/usr/bin/env python3
import PyPDF2
import re
import textwrap

def extract_text_from_pdf(pdf_path):
    """Extrae texto de un archivo PDF"""
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

def find_chapters(text):
    """Encuentra capítulos en el texto basándose en patrones comunes"""
    # Patrones comunes para capítulos
    chapter_patterns = [
        r'(?i)(?:CAPÍTULO|CAPITULO|CAP\.?)\s*(\d+|[IVX]+)',
        r'(?i)(?:SECCIÓN|SECCION)\s*(\d+|[IVX]+)',
        r'^\d+\.\s+[A-Z]',
        r'^[IVX]+\.\s+[A-Z]'
    ]
    
    chapters = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        for pattern in chapter_patterns:
            if re.match(pattern, line.strip()):
                chapters.append((i, line.strip()))
                break
    
    return chapters

def split_into_chapters(text, chapter_markers):
    """Divide el texto en capítulos basándose en los marcadores encontrados"""
    chapters = {}
    lines = text.split('\n')
    
    if not chapter_markers:
        # Si no se encuentran capítulos, trata todo como un solo capítulo
        return {"Documento Completo": text}
    
    for i, (line_num, chapter_title) in enumerate(chapter_markers):
        start = line_num
        end = chapter_markers[i+1][0] if i+1 < len(chapter_markers) else len(lines)
        
        chapter_text = '\n'.join(lines[start:end])
        chapters[chapter_title] = chapter_text
    
    return chapters

def summarize_text(text, max_sentences=5):
    """Crea un resumen básico del texto"""
    # Limpia el texto
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Divide en oraciones
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Toma las primeras oraciones más relevantes
    summary_sentences = []
    for sentence in sentences[:max_sentences * 2]:
        # Prioriza oraciones que contengan palabras clave
        keywords = ['objetivo', 'importante', 'principal', 'conclusión', 'resultado', 
                   'propósito', 'guía', 'modelo', 'agua', 'subterránea']
        if any(keyword in sentence.lower() for keyword in keywords) and len(summary_sentences) < max_sentences:
            summary_sentences.append(sentence)
    
    # Si no hay suficientes oraciones con palabras clave, completa con las primeras
    while len(summary_sentences) < max_sentences and len(sentences) > len(summary_sentences):
        for sentence in sentences:
            if sentence not in summary_sentences:
                summary_sentences.append(sentence)
                break
    
    return '. '.join(summary_sentences[:max_sentences]) + '.'

def main():
    pdf_file = "Guia_uso_modelo_aguas_subterraneas_seia.pdf"
    
    print(f"Extrayendo texto de {pdf_file}...")
    text = extract_text_from_pdf(pdf_file)
    
    # Guarda el texto completo
    with open("texto_completo.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Texto completo guardado en 'texto_completo.txt'")
    
    # Encuentra capítulos
    print("\nBuscando capítulos...")
    chapter_markers = find_chapters(text)
    chapters = split_into_chapters(text, chapter_markers)
    
    # Genera resúmenes
    print(f"\nGenerando resúmenes de {len(chapters)} secciones...")
    
    with open("resumen_por_capitulos.md", "w", encoding="utf-8") as f:
        f.write("# Resumen del documento: Guía uso modelo aguas subterráneas SEIA\n\n")
        
        for chapter_title, chapter_text in chapters.items():
            f.write(f"## {chapter_title}\n\n")
            
            summary = summarize_text(chapter_text)
            # Formatea el resumen
            wrapped_summary = textwrap.fill(summary, width=80)
            f.write(f"{wrapped_summary}\n\n")
            f.write("---\n\n")
    
    print("Resumen guardado en 'resumen_por_capitulos.md'")

if __name__ == "__main__":
    main()