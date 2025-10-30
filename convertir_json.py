#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir archivos JSON con múltiples objetos separados
a un array JSON válido que MongoDB Compass pueda importar
"""

import json
import os

def convert_multi_json_to_array(input_file, output_file):
    """
    Convierte un archivo con múltiples objetos JSON a un array JSON válido
    """
    documents = []
    
    # Leer el archivo con diferentes encodings
    encodings = ['utf-8', 'latin-1', 'iso-8859-1']
    content = None
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding, errors='replace') as f:
                content = f.read()
            break
        except:
            continue
    
    if not content:
        print(f"❌ Error: No se pudo leer {input_file}")
        return 0
    
    # Parsear objetos JSON individuales
    brace_count = 0
    current_obj = ""
    in_string = False
    escape_next = False
    
    for char in content:
        if escape_next:
            current_obj += char
            escape_next = False
            continue
            
        if char == '\\':
            escape_next = True
            current_obj += char
            continue
        
        if char == '"' and not escape_next:
            in_string = not in_string
        
        if not in_string:
            if char == '{':
                if brace_count == 0:
                    current_obj = ""
                brace_count += 1
            elif char == '}':
                brace_count -= 1
        
        current_obj += char
        
        # Cuando cerramos un objeto completo
        if brace_count == 0 and current_obj.strip():
            try:
                obj = json.loads(current_obj.strip())
                documents.append(obj)
                current_obj = ""
            except json.JSONDecodeError:
                current_obj = ""
    
    # Escribir como array JSON válido
    if documents:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
        print(f"✓ Convertido: {os.path.basename(input_file)} → {len(documents)} documentos")
        return len(documents)
    else:
        print(f"❌ No se encontraron documentos en {input_file}")
        return 0

def main():
    print("=" * 80)
    print("CONVERSIÓN DE ARCHIVOS JSON PARA MONGODB COMPASS")
    print("=" * 80)
    
    # Directorios
    input_dir = "./datafiles"
    output_dir = "./datafiles_converted"
    
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Obtener todos los archivos JSON
    json_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.json')])
    
    if not json_files:
        print(f"\n❌ No se encontraron archivos JSON en {input_dir}")
        return
    
    print(f"\n📁 Archivos encontrados: {len(json_files)}")
    print(f"📂 Salida: {output_dir}\n")
    
    total_docs = 0
    
    for filename in json_files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        docs = convert_multi_json_to_array(input_path, output_path)
        total_docs += docs
    
    print("\n" + "=" * 80)
    print(f"✅ CONVERSIÓN COMPLETADA")
    print(f"   • Archivos procesados: {len(json_files)}")
    print(f"   • Total documentos: {total_docs}")
    print(f"   • Ubicación: {output_dir}")
    print("=" * 80)
    
    print("\n📋 SIGUIENTES PASOS:")
    print("1. Abrir MongoDB Compass")
    print("2. Conectar a tu servidor MongoDB")
    print("3. Ir a la base de datos 'streamit_db'")
    print("4. Seleccionar la colección 'invoices'")
    print("5. Click en 'ADD DATA' → 'Import JSON or CSV file'")
    print(f"6. Seleccionar archivos de: {output_dir}")
    print("7. Importar uno por uno o todos juntos\n")

if __name__ == "__main__":
    main()
