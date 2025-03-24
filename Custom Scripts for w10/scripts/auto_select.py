import pyautogui
import time

def unlz_gba_active():
    pyautogui.click(x=3625, y=224)  # Coordinates for "application" button 
    time.sleep(2)

def load_rom():
    # Load the ROM in unLZ-GBA
    pyautogui.click(x=2439, y=282)  # Coordinates for "Open" button
    time.sleep(.1)
    pyautogui.typewrite(r'ROM LOCATION')
    pyautogui.press('enter')
    time.sleep(1)  # Wait for the ROM to load

def save_graphics(num_images):
    for i in range(num_images):
        if i == 0:
            # Save the first graphic
            pyautogui.click(x=2820, y=408)  # Coordinates for "Save As" button 
            time.sleep(.1)
            
            # Select the output directory
            pyautogui.doubleClick(x=2559, y=500)  # Coordinates for "Python auto folder" 
            time.sleep(.1)
            pyautogui.doubleClick(x=2594, y=340)  # Coordinates for "auto select folder"
            time.sleep(.1)
            pyautogui.doubleClick(x=2594, y=340)  # Coordinates for "output folder" 
            time.sleep(.1)

        
        # Save the first graphic
        pyautogui.click(x=2820, y=408)  # Coordinates for "Save As" button 
        time.sleep(.1)    
        # Enter the filename
        pyautogui.click(x=2681, y=614)  # Coordinates for "filename" bar 
        time.sleep(.1)
        pyautogui.typewrite(f'graphic_{i}.png')
        pyautogui.press('enter')
        time.sleep(.25)  # Wait for the save operation to complete

        # Move to the next graphic
        pyautogui.click(x=2820, y=359)  # Coordinates for the "Next" button
        time.sleep(.1)  # Adjust delay as needed

    print("Complete")

def main():
    output_dir = r'OUTPUT'
    num_images = 2087  # Number of images you want to dump

    unlz_gba_active()
    load_rom()
    save_graphics(output_dir, num_images)

if __name__ == '__main__':
    main()
