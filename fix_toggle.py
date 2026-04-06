import glob

files = glob.glob(r'c:\Users\anish\Desktop\work\nm-git\NeuroMentor\flutter\Kivy_Section\neuro_mentor_kivy\screens\*.py')
for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    new_content = content.replace('ToggleShadowButton(', 'ToggleButton(')

    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Fixed ToggleButtons in {filepath}")
