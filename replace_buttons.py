import glob

files = glob.glob(r'c:\Users\anish\Desktop\work\nm-git\NeuroMentor\flutter\Kivy_Section\neuro_mentor_kivy\screens\*.py')
for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    new_content = content.replace('from kivy.uix.button import Button', 'from widgets.custom_ui import ShadowButton')
    new_content = new_content.replace('Button(', 'ShadowButton(')
    new_content = new_content.replace('background_color=', 'bg_color=')

    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Updated {filepath}")
