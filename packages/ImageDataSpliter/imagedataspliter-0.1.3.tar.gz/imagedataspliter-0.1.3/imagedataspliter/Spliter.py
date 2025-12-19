import shutil
import random
from pathlib import Path

def split_dataset(source_folders, output_folder, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, seed=42):
    
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001, "Сума train_ratio, val_ratio, test_ratio має дорівнювати 1"
    
    random.seed(seed)

    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    for source_folder in source_folders:
        source_path = Path(source_folder)
        class_name = source_path.name
        
        print(f"\nОбробка класу: {class_name}")

        all_images = [f for f in source_path.iterdir() 
                     if f.is_file() and f.suffix.lower() in image_extensions]
        
        if not all_images:
            print(f"Попередження: У папці {source_folder} не знайдено зображень")
            continue
            
        random.shuffle(all_images)

        total = len(all_images)
        train_size = int(total * train_ratio)
        val_size = int(total * val_ratio)

        train_files = all_images[:train_size]
        val_files = all_images[train_size:train_size + val_size]
        test_files = all_images[train_size + val_size:]
        
        print(f"  Всього зображень: {total}")
        print(f"  Train: {len(train_files)}, Val: {len(val_files)}, Test: {len(test_files)}")

        for split_name, files in [('train', train_files), ('val', val_files), ('test', test_files)]:
            split_folder = Path(output_folder) / split_name / class_name
            split_folder.mkdir(parents=True, exist_ok=True)
            
            for file in files:
                shutil.copy2(file, split_folder / file.name)
    
    print(f"\n✓ Готово! Дані збережено в: {output_folder}")
    print(f"  Структура: {output_folder}/{{train,val,test}}/{{class_name}}/")

