from pathlib import Path

train_path = Path("../dataset/train")

if not train_path.exists():
    print("❌ Train folder not found!")
    print(f"Looking at: {train_path.absolute()}")
else:
    print("✅ Train folder exists!")
    folders = [d for d in train_path.iterdir() if d.is_dir()]
    print(f"✅ Total classes: {len(folders)}")
    
    total_images = 0
    for folder in folders:
        images = list(folder.glob("*.png")) + list(folder.glob("*.jpg"))
        total_images += len(images)
    
    print(f"✅ Total training images: {total_images}")
    print(f"✅ Average per class: {total_images // len(folders) if len(folders) > 0 else 0}")
    
    print("\n📊 First 5 folders:")
    for folder in sorted(folders)[:5]:
        images = list(folder.glob("*.png")) + list(folder.glob("*.jpg"))
        print(f"   {folder.name}: {len(images)} images")
    
    if len(folders) == 59 and total_images > 20000:
        print("\n🎉 Dataset looks PERFECT! Ready to train!")
    else:
        print(f"\n⚠️ Expected 59 folders, found {len(folders)}")
        print(f"⚠️ Expected ~26,000 images, found {total_images}")
